package com.receiptkeeper.models

import java.io.Serializable

data class ReceiptFields(
    val vendor_name: String? = null,
    val location: String? = null,
    val purchased_at: String? = null,
    val category: String? = null,
    val subtotal: Double? = null,
    val tax: Double? = null,
    val total: Double? = null,
    val currency: String? = null,
    val payment_type: String? = null,
    val card_type: String? = null,
    val card_last4: String? = null,
    val ref_number: String? = null,
    val invoice_number: String? = null,
    val auth_number: String? = null,
    val notes: String? = null
) : Serializable

data class ReceiptExtractionResponse(
    val extraction_id: String,
    val receipt_file_id: String,
    val status: String,
    val extracted: ReceiptFields,
    val confidence: Double? = null,
    val model_name: String,
    val ocr_text: String? = null
) : Serializable

data class ReceiptCreateRequest(
    val receipt_file_id: String,
    val source_extraction_id: String? = null,
    val vendor_name: String? = null,
    val location: String? = null,
    val purchased_at: String? = null,
    val category: String? = null,
    val subtotal: Double? = null,
    val tax: Double? = null,
    val total: Double? = null,
    val currency: String? = null,
    val payment_type: String? = null,
    val card_type: String? = null,
    val card_last4: String? = null,
    val ref_number: String? = null,
    val invoice_number: String? = null,
    val auth_number: String? = null,
    val notes: String? = null
)

data class ReceiptRead(
    val id: String,
    val user_id: String,
    val status: String,
    val vendor_name: String? = null,
    val location: String? = null,
    val purchased_at: String? = null,
    val category: String? = null,
    val subtotal: Double? = null,
    val tax: Double? = null,
    val total: Double? = null,
    val currency: String? = null,
    val payment_type: String? = null,
    val card_type: String? = null,
    val card_last4: String? = null,
    val ref_number: String? = null,
    val invoice_number: String? = null,
    val auth_number: String? = null,
    val notes: String? = null
) : Serializable

data class ReceiptListResponse(
    val items: List<ReceiptRead>,
    val page: Int,
    val page_size: Int,
    val total: Int
)
