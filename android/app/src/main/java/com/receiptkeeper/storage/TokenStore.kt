package com.receiptkeeper.storage

import android.content.Context

class TokenStore(context: Context) {
    private val prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE)

    fun save(accessToken: String, refreshToken: String) {
        prefs.edit()
            .putString("access_token", accessToken)
            .putString("refresh_token", refreshToken)
            .apply()
    }

    fun accessToken(): String? = prefs.getString("access_token", null)

    fun refreshToken(): String? = prefs.getString("refresh_token", null)

    fun clear() {
        prefs.edit().clear().apply()
    }
}
