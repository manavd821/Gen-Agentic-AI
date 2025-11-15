#include <iostream>
#include <chrono>
#include <iomanip>
#include <immintrin.h>

// This version is single-threaded but uses AVX2 intrinsics for vectorization,
// combined with loop unrolling to maximize instruction-level parallelism.
// Since the provided compile command does not include a flag for parallelization
// (like -fopenmp), this single-threaded implementation aims for maximum performance.
double calculate(long long iterations, double param1, double param2) {
    // Vector constants that will be loaded into registers
    const __m256d v_p2 = _mm256_set1_pd(param2);
    const __m256d v_one = _mm256_set1_pd(1.0);
    
    // The loop is optimized by directly incrementing the product `i * param1`
    // instead of incrementing `i` and then multiplying inside the loop.
    // Step for a single vector of 4 doubles
    const __m256d v_step1 = _mm256_set1_pd(4.0 * param1);
    // Step for the unrolled loop (processing 2 vectors, i.e., 8 doubles)
    const __m256d v_step2 = _mm256_set1_pd(8.0 * param1);

    // Two vector accumulators are used to break the dependency chain on the sum,
    // allowing the CPU's out-of-order execution engine to hide instruction latency.
    __m256d v_sum1 = _mm256_setzero_pd();
    __m256d v_sum2 = _mm256_setzero_pd();
    
    // Initialize vectors for `i * param1` for the first two vector operations
    // Note: _mm256_set_pd loads values in reverse order.
    __m256d v_i_mul_p1_a = _mm256_set_pd(4.0 * param1, 3.0 * param1, 2.0 * param1, 1.0 * param1);
    __m256d v_i_mul_p1_b = _mm256_add_pd(v_i_mul_p1_a, v_step1);

    // Process 8 doubles (2 vectors) per loop iteration
    const long long limit_8 = iterations / 8;
    for (long long i = 0; i < limit_8; ++i) {
        // First vector operation (processes 4 doubles)
        const __m256d v_denom_plus_a = _mm256_add_pd(v_i_mul_p1_a, v_p2);
        const __m256d v_denom_minus_a = _mm256_sub_pd(v_i_mul_p1_a, v_p2);
        const __m256d v_term_plus_a = _mm256_div_pd(v_one, v_denom_plus_a);
        const __m256d v_term_minus_a = _mm256_div_pd(v_one, v_denom_minus_a);
        v_sum1 = _mm256_add_pd(v_sum1, _mm256_sub_pd(v_term_plus_a, v_term_minus_a));
        v_i_mul_p1_a = _mm256_add_pd(v_i_mul_p1_a, v_step2);

        // Second vector operation (processes another 4 doubles)
        const __m256d v_denom_plus_b = _mm256_add_pd(v_i_mul_p1_b, v_p2);
        const __m256d v_denom_minus_b = _mm256_sub_pd(v_i_mul_p1_b, v_p2);
        const __m256d v_term_plus_b = _mm256_div_pd(v_one, v_denom_plus_b);
        const __m256d v_term_minus_b = _mm256_div_pd(v_one, v_denom_minus_b);
        v_sum2 = _mm256_add_pd(v_sum2, _mm256_sub_pd(v_term_plus_b, v_term_minus_b));
        v_i_mul_p1_b = _mm256_add_pd(v_i_mul_p1_b, v_step2);
    }
    
    // Combine the two vector accumulators
    v_sum1 = _mm256_add_pd(v_sum1, v_sum2);

    // Horizontally sum the elements in the final vector accumulator
    alignas(32) double h_sum_buffer[4];
    _mm256_store_pd(h_sum_buffer, v_sum1);
    double total_sum = h_sum_buffer[0] + h_sum_buffer[1] + h_sum_buffer[2] + h_sum_buffer[3];

    // Handle the remaining iterations (those not divisible by 8) with a scalar loop
    long long remainder_start = limit_8 * 8 + 1;
    for (long long i = remainder_start; i <= iterations; ++i) {
        total_sum += (1.0 / (i * param1 + param2)) - (1.0 / (i * param1 - param2));
    }

    return 1.0 + total_sum;
}

int main() {
    // Fast I/O, though not strictly necessary for this problem
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    const long long iterations = 200000000;
    const double param1 = 4.0;
    const double param2 = 1.0;
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    double result = calculate(iterations, param1, param2) * 4.0;
    
    auto end_time = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double> elapsed = end_time - start_time;
    
    std::cout << "Result: " << std::fixed << std::setprecision(12) << result << '\n';
    std::cout << "Execution Time: " << std::fixed << std::setprecision(6) << elapsed.count() << " seconds" << '\n';
    
    return 0;
}