import os
import time
from text_processor import TextProcessor

def main():
    """
    Text processing demonstration with multiprocessing and threading.
    
    This implementation demonstrates:
    1. Multiprocessing with Pool
    2. Threading with locks and synchronization
    3. Word statistics computation using both approaches
    """
    
    print("=" * 60)
    print("TEXT PROCESSING WITH CONCURRENCY COMPARISON")
    print("=" * 60)
    print()

    # Initialize processor and data folder
    processor = TextProcessor()
    data_folder = "data"
    output_folder = "output"
    all_results = {}
    
    print("Processing files using different concurrency approaches...\n")
    
    # Method 1: Sequential approach (no concurrency)
    print("1. Testing Sequential Processing (ללא מקביליות)...")
    result_sequential = processor.process_with_sequential(data_folder)
    all_results['sequential'] = result_sequential
    print(f"    Completed in {result_sequential.get('total_time', 0):.4f} seconds")
    print(f"    Processed {len(result_sequential['words'])} words\n")
    
    # Method 2: Multiprocessing approach
    print("2. Testing Multiprocessing ...")
    result1 = processor.process_with_multiprocessing(data_folder)
    all_results['multiprocessing'] = result1
    print(f"    Completed in {result1.get('total_time', 0):.4f} seconds")
    print(f"    Processed {len(result1['words'])} words\n")
    
    # Method 3: Threading approach
    print("3. Testing Threading...")
    result2 = processor.process_with_threading(data_folder)
    all_results['threading'] = result2
    print(f"    Completed in {result2.get('total_time', 0):.4f} seconds")
    print(f"   Processed {len(result2['words'])} words\n")
    
    # Use sequential data for statistics (as baseline reference)
    best_words = result_sequential['words']
    
    print("Using sequential processing data for final analysis...\n")
    
    # Compute statistics using both threading and multiprocessing
    print("4. Computing Statistics with Threading...")
    stats_threading = processor.compute_word_statistics_simple(best_words, 'threading')
    print(f"   Threading computation: {stats_threading.get('computation_time', 0):.4f} seconds\n")
    
    print("5. Computing Statistics with Multiprocessing...")
    stats_multiprocessing = processor.compute_word_statistics_simple(best_words, 'multiprocessing')
    print(f"   Multiprocessing computation: {stats_multiprocessing.get('computation_time', 0):.4f} seconds\n")
    
    # Use threading statistics for final display
    final_stats = stats_threading
    stats_method = "threading"
    
    # Display results
    print("FINAL RESULTS:")
    print("-" * 20)
    print(f"Total words: {final_stats['total_words']:,}")
    print(f"Unique words: {final_stats['unique_words']:,}")
    print(f"Statistics computed using: {stats_method}")
    print()
    print("Top 10 most common words:")
    for i, (word, count) in enumerate(final_stats['top_10'], 1):
        print(f"  {i:2d}. {word:<12} : {count:,}")
    print()
    
    # Write comprehensive output files
    print("6. Writing Output Files...")
    processor.write_output_files(all_results, output_folder)
    
    # Write traditional output files for compatibility
    write_traditional_output_files(final_stats, output_folder)
    
    print(f"\n All output files written to '{output_folder}' folder")
    print("\nFiles created:")
    print("  - vocabulary.txt (sorted unique words)")
    print("  - vocabulary_stats.txt (traditional format)")
    print("  - performance_comparison.txt (detailed analysis)")
    
    # Performance summary
    print("\nPERFORMANCE SUMMARY:")
    print("-" * 40)
    
    # Sort results by total_time for comparison
    sorted_results = sorted(all_results.items(), key=lambda x: x[1].get('total_time', float('inf')))
    
    for method, result in sorted_results:
        total_time = result.get('total_time', 0)
        processing_time = result.get('processing_time', 0)
        words_count = len(result['words'])
        
        print(f"{method.capitalize():<15}:")
        print(f"  Total Time:      {total_time:.4f} seconds")
        if processing_time > 0:
            print(f"  Processing Time: {processing_time:.4f} seconds")
            overhead = total_time - processing_time
            print(f"  Overhead Time:   {overhead:.4f} seconds")
        print(f"  Words Processed: {words_count:,}")
        if total_time > 0:
            print(f"  Words/Second:    {words_count/total_time:.0f}")
        print()
    
    # Show speed comparison
    if len(sorted_results) > 1:
        fastest_time = sorted_results[0][1].get('total_time', 0)
        print("Speed Comparison:")
        print("-" * 16)
        for i, (method, result) in enumerate(sorted_results):
            total_time = result.get('total_time', 0)
            if i == 0:
                print(f"{method.capitalize():<15}: 1.00x (fastest)")
            elif fastest_time > 0:
                speedup = total_time / fastest_time
                print(f"{method.capitalize():<15}: {speedup:.2f}x slower")


def write_traditional_output_files(stats, output_folder="output"):
    """Write the traditional vocabulary and statistics files for compatibility."""
    # 1. vocabulary.txt: unique words sorted alphabetically
    vocab_path = os.path.join(output_folder, "vocabulary.txt")
    with open(vocab_path, 'w', encoding='utf-8') as f:
        for word in sorted(stats['frequencies']):
            f.write(word + "\n")

    # 2. vocabulary_stats.txt: statistics summary
    stats_path = os.path.join(output_folder, "vocabulary_stats.txt")
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(f"Total words: {stats['total_words']}\n")
        f.write(f"Unique words: {stats['unique_words']}\n\n")
        f.write("Top 10 most common words:\n")
        for i, (word, count) in enumerate(stats['top_10'], start=1):
            f.write(f"{i}. {word} {count}\n")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.4f} seconds")
