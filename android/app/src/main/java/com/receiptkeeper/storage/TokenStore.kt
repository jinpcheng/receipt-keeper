package com.receiptkeeper.storage

import android.content.Context
import android.util.Base64
import org.json.JSONObject

class TokenStore(context: Context) {
    private val prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE)

    fun save(accessToken: String, refreshToken: String) {
        prefs.edit()
            .putString("access_token", accessToken)
            .putString("refresh_token", refreshToken)
            .apply()
    }

    fun saveAccessToken(accessToken: String) {
        prefs.edit().putString("access_token", accessToken).apply()
    }

    fun accessToken(): String? = prefs.getString("access_token", null)

    fun refreshToken(): String? = prefs.getString("refresh_token", null)

    fun isAccessTokenExpired(skewSeconds: Long = 30): Boolean {
        val token = accessToken() ?: return true
        val exp = jwtExpSeconds(token) ?: return true
        val now = System.currentTimeMillis() / 1000L
        return exp <= (now + skewSeconds)
    }

    fun clear() {
        prefs.edit().clear().apply()
    }

    private fun jwtExpSeconds(jwt: String): Long? {
        // JWT: header.payload.signature (Base64URL).
        val parts = jwt.split(".")
        if (parts.size < 2) return null
        return try {
            val payloadJson = String(Base64.decode(parts[1], Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING))
            JSONObject(payloadJson).optLong("exp").takeIf { it > 0 }
        } catch (_: Exception) {
            null
        }
    }
}
