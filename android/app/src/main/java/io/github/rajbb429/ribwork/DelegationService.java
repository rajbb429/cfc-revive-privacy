package io.github.rajbb429.ribwork;


import com.google.androidbrowserhelper.playbilling.digitalgoods.DigitalGoodsRequestHandler;


public class DelegationService extends
        com.google.androidbrowserhelper.trusted.DelegationService {
    @Override
    public void onCreate() {
        super.onCreate();

        // Acknowledge purchases first (it passes every request on), then answer the web app.
        registerExtraCommandHandler(new PurchaseAcknowledger(getApplicationContext()));
        registerExtraCommandHandler(new DigitalGoodsRequestHandler(getApplicationContext()));
    }
}

