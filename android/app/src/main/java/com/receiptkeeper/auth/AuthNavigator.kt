package com.receiptkeeper.auth

import android.app.Activity
import android.content.Intent
import com.receiptkeeper.AuthActivity
import com.receiptkeeper.storage.TokenStore

object AuthNavigator {
    fun goToLogin(activity: Activity) {
        TokenStore(activity).clear()
        val intent = Intent(activity, AuthActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        activity.startActivity(intent)
        activity.finish()
    }
}

