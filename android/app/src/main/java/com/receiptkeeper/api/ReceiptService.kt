package com.receiptkeeper.api

import com.receiptkeeper.models.ReceiptCreateRequest
import com.receiptkeeper.models.ReceiptExtractionResponse
import com.receiptkeeper.models.ReceiptListResponse
import com.receiptkeeper.models.ReceiptRead
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.GET
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query
import retrofit2.http.PATCH
import retrofit2.http.Path

interface ReceiptService {
    @Multipart
    @POST("receipts/extractions")
    suspend fun createExtraction(
        @Part file: MultipartBody.Part,
        @Part("currency") currency: RequestBody?
    ): ReceiptExtractionResponse

    @POST("receipts")
    suspend fun createReceipt(@Body payload: ReceiptCreateRequest): ReceiptRead

    @GET("receipts")
    suspend fun listReceipts(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20
    ): ReceiptListResponse

    @PATCH("receipts/{id}")
    suspend fun updateReceipt(
        @Path("id") id: String,
        @Body payload: Map<String, Any?>
    ): ReceiptRead
}
