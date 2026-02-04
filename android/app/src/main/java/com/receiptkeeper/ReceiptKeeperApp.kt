package com.receiptkeeper

import android.app.Application
import com.receiptkeeper.api.ApiClient

class ReceiptKeeperApp : Application() {
    override fun onCreate() {
        super.onCreate()
        ApiClient.init(this)
    }
}
