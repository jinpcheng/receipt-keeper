package com.receiptkeeper.api

import com.receiptkeeper.models.ReceiptCreateRequest
import com.receiptkeeper.models.ReceiptExtractionResponse
import com.receiptkeeper.models.ReceiptRead
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface ReceiptService {
    @Multipart
    @POST("receipts/extractions")
    suspend fun createExtraction(
        @Part file: MultipartBody.Part,
        @Part("currency") currency: RequestBody?
    ): ReceiptExtractionResponse

    @POST("receipts")
    suspend fun createReceipt(@Body payload: ReceiptCreateRequest): ReceiptRead
}
