package com.receiptkeeper

import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.receiptkeeper.api.ApiClient
import com.receiptkeeper.models.ReceiptRead
import kotlinx.coroutines.launch
import java.io.Serializable

class ReceiptDetailActivity : AppCompatActivity() {
    private lateinit var receipt: ReceiptRead

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_receipt_detail)

        val extra = getSerializableCompat(EXTRA_RECEIPT, ReceiptRead::class.java)
        if (extra == null) {
            finish()
            return
        }
        receipt = extra

        val vendor = findViewById<EditText>(R.id.detail_vendor)
        val total = findViewById<EditText>(R.id.detail_total)
        val notes = findViewById<EditText>(R.id.detail_notes)
        val status = findViewById<TextView>(R.id.detail_status)
        val save = findViewById<Button>(R.id.detail_save)

        vendor.setText(receipt.vendor_name ?: "")
        total.setText(receipt.total?.toString() ?: "")
        notes.setText(receipt.notes ?: "")

        save.setOnClickListener {
            val newVendor = vendor.text.toString().trim()
            val newTotal = total.text.toString().toDoubleOrNull()
            val newNotes = notes.text.toString()

            lifecycleScope.launch {
                try {
                    ApiClient.receiptService.updateReceipt(
                        receipt.id,
                        mapOf(
                            "vendor_name" to newVendor,
                            "total" to newTotal,
                            "notes" to newNotes
                        )
                    )
                    status.text = getString(R.string.detail_saved)
                } catch (ex: Exception) {
                    status.text = getString(R.string.detail_save_failed)
                }
            }
        }
    }

    companion object {
        const val EXTRA_RECEIPT = "extra_receipt"
    }

    private fun <T : Serializable> getSerializableCompat(key: String, clazz: Class<T>): T? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getSerializableExtra(key, clazz)
        } else {
            @Suppress("DEPRECATION")
            intent.getSerializableExtra(key)?.let { value ->
                if (clazz.isInstance(value)) clazz.cast(value) else null
            }
        }
    }
}
