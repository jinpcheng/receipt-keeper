package com.receiptkeeper

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.receiptkeeper.api.ApiClient
import com.receiptkeeper.models.ReceiptCreateRequest
import com.receiptkeeper.models.ReceiptExtractionResponse
import kotlinx.coroutines.launch

class ReviewActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_review)

        val extraction = intent.getSerializableExtra(EXTRA_EXTRACTION) as? ReceiptExtractionResponse
        val content = findViewById<TextView>(R.id.review_content)
        val saveButton = findViewById<Button>(R.id.review_save)
        val backButton = findViewById<Button>(R.id.review_back)

        if (extraction == null) {
            content.text = getString(R.string.review_save_failed)
            saveButton.isEnabled = false
            return
        }

        content.text = buildSummary(extraction)

        backButton.setOnClickListener { finish() }
        saveButton.setOnClickListener {
            saveReceipt(extraction, content)
        }
    }

    private fun buildSummary(extraction: ReceiptExtractionResponse): String {
        val fields = extraction.extracted
        return listOf(
            "Vendor: ${fields.vendor_name ?: "-"}",
            "Location: ${fields.location ?: "-"}",
            "Date: ${fields.purchased_at ?: "-"}",
            "Category: ${fields.category ?: "-"}",
            "Subtotal: ${fields.subtotal ?: "-"}",
            "Tax: ${fields.tax ?: "-"}",
            "Total: ${fields.total ?: "-"}",
            "Currency: ${fields.currency ?: "-"}",
            "Payment: ${fields.payment_type ?: "-"}",
            "Card: ${fields.card_type ?: "-"} ${fields.card_last4 ?: ""}",
            "Ref#: ${fields.ref_number ?: "-"}",
            "Invoice#: ${fields.invoice_number ?: "-"}",
            "Auth#: ${fields.auth_number ?: "-"}",
            "Notes: ${fields.notes ?: "-"}"
        ).joinToString("\n")
    }

    private fun saveReceipt(extraction: ReceiptExtractionResponse, content: TextView) {
        val fields = extraction.extracted
        val request = ReceiptCreateRequest(
            receipt_file_id = extraction.receipt_file_id,
            source_extraction_id = extraction.extraction_id,
            vendor_name = fields.vendor_name,
            location = fields.location,
            purchased_at = fields.purchased_at,
            category = fields.category,
            subtotal = fields.subtotal,
            tax = fields.tax,
            total = fields.total,
            currency = fields.currency,
            payment_type = fields.payment_type,
            card_type = fields.card_type,
            card_last4 = fields.card_last4,
            ref_number = fields.ref_number,
            invoice_number = fields.invoice_number,
            auth_number = fields.auth_number,
            notes = fields.notes
        )

        lifecycleScope.launch {
            try {
                ApiClient.receiptService.createReceipt(request)
                content.text = getString(R.string.review_saved)
            } catch (ex: Exception) {
                content.text = getString(R.string.review_save_failed)
            }
        }
    }

    companion object {
        const val EXTRA_EXTRACTION = "extra_extraction"
    }
}
