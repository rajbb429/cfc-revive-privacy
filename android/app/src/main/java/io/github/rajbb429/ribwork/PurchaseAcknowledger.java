package io.github.rajbb429.ribwork;

import android.content.Context;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.browser.trusted.TrustedWebActivityCallbackRemote;

import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.QueryPurchasesParams;
import com.google.androidbrowserhelper.trusted.ExtraCommandHandler;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Acknowledges one-time purchases (the full-app unlock, including redeemed promo codes) on the
 * device. Google Play refunds and revokes any purchase that isn't acknowledged within 3 days, and
 * the web app can't acknowledge through the Digital Goods API, so the Android side does it.
 *
 * Registered ahead of the Digital Goods handler: every time the web app asks Play about products
 * or purchases (at launch, when it comes back into view, after buying or redeeming a code), this
 * sweeps for unacknowledged purchases, then lets the Digital Goods handler answer the request.
 */
public class PurchaseAcknowledger implements ExtraCommandHandler {
    private static final String TAG = "RibworkPurchases";
    private static final long MIN_INTERVAL_MS = 3000;

    private final Context mContext;
    private long mLastSweep;

    public PurchaseAcknowledger(Context context) {
        mContext = context.getApplicationContext();
    }

    @NonNull
    @Override
    public Bundle handleExtraCommand(Context context, String commandName, Bundle args,
            @Nullable TrustedWebActivityCallbackRemote callback) {
        sweep();
        // Not handled here: the Digital Goods handler answers the web app's request.
        Bundle result = new Bundle();
        result.putBoolean(EXTRA_COMMAND_SUCCESS, false);
        return result;
    }

    /** Finds purchased-but-unacknowledged one-time products and acknowledges them. */
    public synchronized void sweep() {
        long now = SystemClock.elapsedRealtime();
        if (mLastSweep != 0 && now - mLastSweep < MIN_INTERVAL_MS) return;
        mLastSweep = now;

        BillingClient client = BillingClient.newBuilder(mContext)
                .setListener((billingResult, purchases) -> { })
                .enablePendingPurchases(PendingPurchasesParams.newBuilder()
                        .enableOneTimeProducts()
                        .build())
                .build();

        client.startConnection(new BillingClientStateListener() {
            @Override
            public void onBillingSetupFinished(@NonNull BillingResult setup) {
                if (setup.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                    Log.w(TAG, "Billing unavailable: " + setup.getDebugMessage());
                    client.endConnection();
                    return;
                }
                QueryPurchasesParams query = QueryPurchasesParams.newBuilder()
                        .setProductType(BillingClient.ProductType.INAPP)
                        .build();
                client.queryPurchasesAsync(query, (result, purchases) -> {
                    List<Purchase> pending = new ArrayList<>();
                    for (Purchase p : purchases) {
                        if (p.getPurchaseState() == Purchase.PurchaseState.PURCHASED
                                && !p.isAcknowledged()) {
                            pending.add(p);
                        }
                    }
                    if (pending.isEmpty()) {
                        client.endConnection();
                        return;
                    }
                    AtomicInteger left = new AtomicInteger(pending.size());
                    for (Purchase p : pending) {
                        AcknowledgePurchaseParams ack = AcknowledgePurchaseParams.newBuilder()
                                .setPurchaseToken(p.getPurchaseToken())
                                .build();
                        client.acknowledgePurchase(ack, ackResult -> {
                            Log.i(TAG, "Acknowledged " + p.getProducts() + ": "
                                    + ackResult.getResponseCode());
                            if (left.decrementAndGet() == 0) client.endConnection();
                        });
                    }
                });
            }

            @Override
            public void onBillingServiceDisconnected() { }
        });
    }
}
