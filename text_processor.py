import os
import string
import threading
import multiprocessing
import time

# Simple word counter function (replaces Counter)
def count_words_simple(words):
    """Simple word counter using dictionary."""
    counter = {}
    for word in words:
        counter[word] = counter.get(word, 0) + 1
    return counter

def merge_counters(counter_list):
    """Merge multiple word counters."""
    result = {}
    for counter in counter_list:
        for word, count in counter.items():
            result[word] = result.get(word, 0) + count
    return result

def get_top_words(counter, n=10):
    """Get top N most common words."""
    sorted_words = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:n]

# Standalone functions for multiprocessing (must be picklable)
def read_and_clean_file_standalone(filepath):
    """Standalone function for multiprocessing - reads and cleans a single file."""
    start_time = time.time()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read().lower()

        # Remove punctuation and digits
        translator = str.maketrans('', '', string.punctuation)
        cleaned_text = text.translate(translator)

        # Keep only alphabetic words
        words = [word for word in cleaned_text.split() if word.isalpha()]
        
        processing_time = time.time() - start_time
        print(f"[INFO] Processed {os.path.basename(filepath)}: {len(words)} words in {processing_time:.4f} seconds")
        return filepath, words, processing_time

    except Exception as e:
        processing_time = time.time() - start_time
        print(f"[ERROR] Error reading {filepath}: {e}")
        return filepath, [], processing_time

def count_chunk_standalone(chunk):
    """Standalone function for multiprocessing word counting."""
    return count_words_simple(chunk)

class TextProcessor:
    def __init__(self):
        self.results = {}
        self.lock = threading.Lock()
        self.processed_files = 0
        
    def read_and_clean_file(self, filepath):
        """Reads a single file, cleans its text, and returns (filepath, list of words, processing_time)."""
        start_time = time.time()
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read().lower()

            # Remove punctuation and digits
            translator = str.maketrans('', '', string.punctuation)
            cleaned_text = text.translate(translator)

            # Keep only alphabetic words
            words = [word for word in cleaned_text.split() if word.isalpha()]
            
            processing_time = time.time() - start_time
            print(f"[INFO] Processed {os.path.basename(filepath)}: {len(words)} words in {processing_time:.4f} seconds")
            return filepath, words, processing_time

        except Exception as e:
            processing_time = time.time() - start_time
            print(f"[ERROR] Error reading {filepath}: {e}")
            return filepath, [], processing_time

    def process_with_multiprocessing(self, folder_path):
        """Process files using multiprocessing with Pool."""
        print("[INFO] Starting multiprocessing approach...")
        start_time = time.time()
        
        filepaths = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.endswith(".txt")
        ]

        all_words = []
        total_processing_time = 0

        with multiprocessing.Pool(4) as pool:  # Use fixed number of processes
            results = pool.map(read_and_clean_file_standalone, filepaths)

        for filepath, words, proc_time in results:
            all_words.extend(words)
            total_processing_time += proc_time

        total_time = time.time() - start_time
        print(f"[INFO] Multiprocessing completed in {total_time:.4f} seconds")
        
        return {
            'words': all_words,
            'method': 'multiprocessing',
            'total_time': total_time,
            'processing_time': total_processing_time
        }

    def process_with_threading(self, folder_path):
        """Process files using threading."""
        print("[INFO] Starting threading approach...")
        start_time = time.time()
        
        filepaths = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.endswith(".txt")
        ]

        all_words = []
        results = []
        threads = []
        total_processing_time = 0

        def worker(filepath, results, index):
            result = self.read_and_clean_file(filepath)
            with self.lock:
                results[index] = result

        # Prepare results list
        results = [None] * len(filepaths)

        # Create and start threads
        for i, filepath in enumerate(filepaths):
            thread = threading.Thread(target=worker, args=(filepath, results, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results
        for result in results:
            if result:
                filepath, words, proc_time = result
                all_words.extend(words)
                total_processing_time += proc_time

        total_time = time.time() - start_time
        print(f"[INFO] Threading completed in {total_time:.4f} seconds")
        
        return {
            'words': all_words,
            'method': 'threading',
            'total_time': total_time,
            'processing_time': total_processing_time
        }

    def process_with_sequential(self, folder_path):
        """Process files using sequential approach (no concurrency)."""
        print("[INFO] Starting sequential approach...")
        start_time = time.time()
        
        filepaths = [
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.endswith(".txt")
        ]

        all_words = []
        total_processing_time = 0

        # Process files one by one sequentially
        for filepath in filepaths:
            filepath_result, words, proc_time = self.read_and_clean_file(filepath)
            all_words.extend(words)
            total_processing_time += proc_time

        total_time = time.time() - start_time
        print(f"[INFO] Sequential processing completed in {total_time:.4f} seconds")
        
        return {
            'words': all_words,
            'method': 'sequential',
            'total_time': total_time,
            'processing_time': total_processing_time
        }

    def compute_word_statistics_simple(self, words, method='threading'):
        """Compute word statistics using simple counting."""
        print(f"[INFO] Computing statistics using {method}...")
        start_time = time.time()
        
        # Use simple single-threaded approach for consistent results
        total_counter = count_words_simple(words)
        
        computation_time = time.time() - start_time
        print(f"[INFO] Statistics computation completed in {computation_time:.4f} seconds")
        
        return {
            'total_words': sum(total_counter.values()),
            'unique_words': len(total_counter),
            'frequencies': total_counter,
            'top_10': get_top_words(total_counter, 10),
            'computation_time': computation_time
        }

    def _compute_stats_threading_simple(self, words):
        """Compute statistics using threading with simple counting."""
        print("[INFO] Computing statistics using threading...")
        start_time = time.time()
        
        chunk_size = len(words) // 4  # Use 4 threads
        word_chunks = []
        
        # Create chunks and ensure all words are included
        for i in range(0, len(words), chunk_size):
            if i + chunk_size < len(words):
                word_chunks.append(words[i:i + chunk_size])
            else:
                # Last chunk gets all remaining words
                word_chunks.append(words[i:])
                break
        
        results = [None] * len(word_chunks)
        threads = []
        
        def count_words(chunk, results, index):
            counter = count_words_simple(chunk)
            results[index] = counter
        
        # Create and start threads
        for i, chunk in enumerate(word_chunks):
            thread = threading.Thread(target=count_words, args=(chunk, results, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Merge results
        total_counter = merge_counters([r for r in results if r is not None])
        
        computation_time = time.time() - start_time
        print(f"[INFO] Threading statistics computation completed in {computation_time:.4f} seconds")
        
        return {
            'total_words': sum(total_counter.values()),
            'unique_words': len(total_counter),
            'frequencies': total_counter,
            'top_10': get_top_words(total_counter, 10),
            'computation_time': computation_time
        }

    def _compute_stats_multiprocessing_simple(self, words):
        """Compute statistics using multiprocessing with simple counting."""
        print("[INFO] Computing statistics using multiprocessing...")
        start_time = time.time()
        
        chunk_size = len(words) // 4  # Use 4 processes
        word_chunks = []
        
        # Create chunks and ensure all words are included
        for i in range(0, len(words), chunk_size):
            if i + chunk_size < len(words):
                word_chunks.append(words[i:i + chunk_size])
            else:
                # Last chunk gets all remaining words
                word_chunks.append(words[i:])
                break
        
        with multiprocessing.Pool(4) as pool:
            counters = pool.map(count_chunk_standalone, word_chunks)
        
        # Merge all counters
        total_counter = merge_counters(counters)
        
        computation_time = time.time() - start_time
        print(f"[INFO] Multiprocessing statistics computation completed in {computation_time:.4f} seconds")
        
        return {
            'total_words': sum(total_counter.values()),
            'unique_words': len(total_counter),
            'frequencies': total_counter,
            'top_10': get_top_words(total_counter, 10),
            'computation_time': computation_time
        }

    def write_output_files(self, all_results, output_folder="output"):
        """Write comprehensive output files with performance comparison."""
        os.makedirs(output_folder, exist_ok=True)
        
        # Get the best result (use first available method's data)
        primary_method = list(all_results.keys())[0]
        words = all_results[primary_method]['words']
        
        # Compute final statistics for output
        word_counter = count_words_simple(words)
        top_words = get_top_words(word_counter, 10)
        unique_words = sorted(word_counter.keys())
        
        # 1. Write vocabulary.txt (sorted unique words)
        vocab_path = os.path.join(output_folder, "vocabulary.txt")
        with open(vocab_path, 'w', encoding='utf-8') as f:
            for word in unique_words:
                f.write(f"{word}\n")
        
        # 2. Write vocabulary_stats.txt (traditional format)
        stats_path = os.path.join(output_folder, "vocabulary_stats.txt")
        with open(stats_path, 'w', encoding='utf-8') as f:
            f.write(f"Total words: {len(words)}\n")
            f.write(f"Unique words: {len(unique_words)}\n\n")
            f.write("Top 10 most common words:\n")
            for i, (word, count) in enumerate(top_words, start=1):
                f.write(f"{i}. {word} – {count}\n")
            f.write("\n")
        
        # 3. Performance comparison report with detailed timing
        comparison_path = os.path.join(output_folder, "performance_comparison.txt")
        with open(comparison_path, 'w', encoding='utf-8') as f:
            f.write("CONCURRENCY PERFORMANCE COMPARISON REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"System Information:\n")
            f.write(f"- CPU Cores: 4 (fixed pool size)\n\n")
            
            f.write("Processing Method Performance:\n")
            f.write("-" * 40 + "\n")
            
            # Sort methods by total time for comparison
            sorted_methods = sorted(all_results.items(), 
                                  key=lambda x: x[1].get('total_time', float('inf')))
            
            for method, result in sorted_methods:
                f.write(f"Method: {method}\n")
                f.write(f"  Words Processed: {len(result['words'])}\n")
                if 'total_time' in result:
                    f.write(f"  Total Time: {result['total_time']:.4f} seconds\n")
                if 'computation_time' in result:
                    f.write(f"  Statistics Computation Time: {result['computation_time']:.4f} seconds\n")
                f.write("\n")
            
        print(f"\n[INFO] Output files written to '{output_folder}' folder")
        print("Files created:")
        print("  - vocabulary.txt (sorted unique words)")
        print("  - vocabulary_stats.txt (traditional format)")
        print("  - performance_comparison.txt (detailed timing analysis)")

