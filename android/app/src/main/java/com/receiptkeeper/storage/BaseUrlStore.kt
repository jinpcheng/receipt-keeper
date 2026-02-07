package com.receiptkeeper.storage

import android.content.Context

import com.receiptkeeper.BuildConfig

class BaseUrlStore(context: Context) {
    private val prefs = context.getSharedPreferences("settings", Context.MODE_PRIVATE)

    fun get(): String {
        val raw = prefs.getString("api_base_url", null)
        return normalize(raw ?: BuildConfig.API_BASE_URL)
    }

    fun save(value: String) {
        val normalized = normalize(value)
        prefs.edit().putString("api_base_url", normalized).apply()
    }

    companion object {
        fun normalize(input: String): String {
            var url = input.trim()
            if (url.isBlank()) {
                return BuildConfig.API_BASE_URL
            }
            if (!url.endsWith("/")) {
                url += "/"
            }
            // Accept either host root (http://x:8081/) or the API root (..../api/v1/).
            if (!url.contains("/api/")) {
                url += "api/v1/"
            } else if (!url.endsWith("api/v1/")) {
                // Try to normalize common variants.
                url = url.replace(Regex("/api/v1/?$"), "/api/v1/")
            }
            if (!url.endsWith("/")) {
                url += "/"
            }
            return url
        }
    }
}

