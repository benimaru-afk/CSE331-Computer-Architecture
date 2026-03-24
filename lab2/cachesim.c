/******************************************************************************
 *
 * @file cachesim.c
 * @brief A simple cache simulator that models different cache configurations
 *        and tracks performance statistics based on memory access traces.
 *
 * @author Benjamin Mannal
 * @date Assigned: 3/3/2026 | Due: 3/24/2026
 *
 ******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>

/**
 * @brief Represents a single cache line.
 *
 * Stores whether the line is valid, its tag, and ordering info
 * used for FIFO replacement.
 */
typedef struct {
    int valid;
    uint32_t tag;
    uint32_t fifo_order;
} CacheLine;

/**
 * @brief Represents a cache set.
 *
 * Contains multiple cache lines and a counter to track
 * insertion order for FIFO replacement.
 */
typedef struct {
    CacheLine *lines;
    uint32_t fifo_counter;
} CacheSet;

/**
 * @brief Represents the full cache structure.
 *
 * Holds all sets along with configuration parameters
 * such as associativity, line size, and policies.
 */
typedef struct {
    CacheSet *sets;
    int num_sets;
    int associativity;
    int line_size;
    int replacement_policy;
    int miss_penalty;
    int write_allocate;
} Cache;

/**
 * @brief Tracks statistics for cache simulation.
 *
 * Keeps counts of accesses, hits, and cycle-related metrics.
 */
typedef struct {
    uint64_t total_accesses;
    uint64_t total_hits;
    uint64_t load_accesses;
    uint64_t load_hits;
    uint64_t store_accesses;
    uint64_t store_hits;
    uint64_t total_cycles;
    uint64_t total_mem_access_cycles;
} Stats;

/**
 * @brief Allocates and initializes a cache based on given parameters.
 */
Cache* create_cache(int line_size, int associativity, int data_size_kb, 
                    int replacement_policy, int miss_penalty, int write_allocate);

/**
 * @brief Frees all memory associated with a cache.
 */
void free_cache(Cache *cache);

/**
 * @brief Simulates a cache access and determines hit or miss.
 *
 * @return 1 if hit, 0 if miss
 */
int access_cache(Cache *cache, uint32_t address, char access_type, Stats *stats);

/**
 * @brief Reads cache configuration values from a file.
 */
void parse_config(const char *filename, int *line_size, int *associativity, 
                  int *data_size_kb, int *replacement_policy, 
                  int *miss_penalty, int *write_allocate);

/**
 * @brief Processes a memory trace file and updates statistics.
 */
void process_trace(Cache *cache, const char *trace_filename, Stats *stats);

/**
 * @brief Writes simulation results to an output file.
 */
void write_output(const char *filename, Stats *stats);

/**
 * @brief Extracts the set index from a memory address.
 */
uint32_t get_set_index(Cache *cache, uint32_t address);

/**
 * @brief Extracts the tag from a memory address.
 */
uint32_t get_tag(Cache *cache, uint32_t address);

/**
 * @brief Computes integer log base 2.
 */
int log2_int(int value);

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <config_file> <trace_file>\n", argv[0]);
        return 1;
    }

    /**
     * @brief Seed random number generator for random replacement policy.
     */
    srand(time(NULL));

    int line_size, associativity, data_size_kb;
    int replacement_policy, miss_penalty, write_allocate;
    
    parse_config(argv[1], &line_size, &associativity, &data_size_kb, 
                 &replacement_policy, &miss_penalty, &write_allocate);

    Cache *cache = create_cache(line_size, associativity, data_size_kb, 
                                replacement_policy, miss_penalty, write_allocate);

    if (cache == NULL) {
        fprintf(stderr, "Error: Failed to create cache\n");
        return 1;
    }

    Stats stats = {0};

    char output_filename[256];
    snprintf(output_filename, sizeof(output_filename), "%s.out", argv[2]);

    process_trace(cache, argv[2], &stats);
    write_output(output_filename, &stats);

    free_cache(cache);

    return 0;
}

/**
 * @brief Builds and initializes a cache structure.
 *
 * Determines number of sets and allocates memory for all sets and lines.
 */
Cache* create_cache(int line_size, int associativity, int data_size_kb, 
                    int replacement_policy, int miss_penalty, int write_allocate) {
    Cache *cache = (Cache *)malloc(sizeof(Cache));
    if (cache == NULL) return NULL;

    cache->line_size = line_size;
    cache->replacement_policy = replacement_policy;
    cache->miss_penalty = miss_penalty;
    cache->write_allocate = write_allocate;

    int total_data_size = data_size_kb * 1024;
    int num_lines = total_data_size / line_size;

    if (associativity == 0) {
        cache->num_sets = 1;
        cache->associativity = num_lines;
    } else {
        cache->associativity = associativity;
        cache->num_sets = num_lines / associativity;
    }

    cache->sets = (CacheSet *)malloc(cache->num_sets * sizeof(CacheSet));
    if (cache->sets == NULL) {
        free(cache);
        return NULL;
    }

    for (int i = 0; i < cache->num_sets; i++) {
        cache->sets[i].lines = (CacheLine *)calloc(cache->associativity, sizeof(CacheLine));
        cache->sets[i].fifo_counter = 0;
        if (cache->sets[i].lines == NULL) {
            for (int j = 0; j < i; j++) {
                free(cache->sets[j].lines);
            }
            free(cache->sets);
            free(cache);
            return NULL;
        }
    }

    return cache;
}

/**
 * @brief Releases all dynamically allocated cache memory.
 */
void free_cache(Cache *cache) {
    if (cache == NULL) return;
    
    for (int i = 0; i < cache->num_sets; i++) {
        free(cache->sets[i].lines);
    }
    free(cache->sets);
    free(cache);
}

/**
 * @brief Computes log base 2 using bit shifting.
 */
int log2_int(int value) {
    int result = 0;
    while (value > 1) {
        value >>= 1;
        result++;
    }
    return result;
}

/**
 * @brief Determines which cache set an address maps to.
 */
uint32_t get_set_index(Cache *cache, uint32_t address) {
    int offset_bits = log2_int(cache->line_size);
    int set_bits = log2_int(cache->num_sets);
    
    uint32_t set_index = (address >> offset_bits) & ((1 << set_bits) - 1);
    return set_index;
}

/**
 * @brief Extracts the tag bits from a memory address.
 */
uint32_t get_tag(Cache *cache, uint32_t address) {
    int offset_bits = log2_int(cache->line_size);
    int set_bits = log2_int(cache->num_sets);
    
    uint32_t tag = address >> (offset_bits + set_bits);
    return tag;
}

/**
 * @brief Simulates accessing the cache.
 *
 * Handles hits, misses, replacement policy, and updates timing stats.
 */
int access_cache(Cache *cache, uint32_t address, char access_type, Stats *stats) {
    uint32_t set_index = get_set_index(cache, address);
    uint32_t tag = get_tag(cache, address);
    
    CacheSet *set = &cache->sets[set_index];
    
    for (int i = 0; i < cache->associativity; i++) {
        if (set->lines[i].valid && set->lines[i].tag == tag) {
            stats->total_mem_access_cycles += 1;
            return 1;
        }
    }
    
    if (access_type == 's' && cache->write_allocate == 0) {
        stats->total_mem_access_cycles += 1 + cache->miss_penalty;
        return 0;
    }
    
    int replace_index = -1;
    
    for (int i = 0; i < cache->associativity; i++) {
        if (!set->lines[i].valid) {
            replace_index = i;
            break;
        }
    }
    
    if (replace_index == -1) {
        if (cache->replacement_policy == 0) {
            replace_index = rand() % cache->associativity;
        } else {
            uint32_t oldest_order = set->lines[0].fifo_order;
            replace_index = 0;
            for (int i = 1; i < cache->associativity; i++) {
                if (set->lines[i].fifo_order < oldest_order) {
                    oldest_order = set->lines[i].fifo_order;
                    replace_index = i;
                }
            }
        }
    }
    
    set->lines[replace_index].valid = 1;
    set->lines[replace_index].tag = tag;
    set->lines[replace_index].fifo_order = set->fifo_counter++;
    
    stats->total_mem_access_cycles += 1 + cache->miss_penalty;
    return 0;
}

/**
 * @brief Reads cache configuration parameters from file.
 */
void parse_config(const char *filename, int *line_size, int *associativity, 
                  int *data_size_kb, int *replacement_policy, 
                  int *miss_penalty, int *write_allocate) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot open config file %s\n", filename);
        exit(1);
    }

    if (fscanf(file, "%d", line_size) != 1 ||
        fscanf(file, "%d", associativity) != 1 ||
        fscanf(file, "%d", data_size_kb) != 1 ||
        fscanf(file, "%d", replacement_policy) != 1 ||
        fscanf(file, "%d", miss_penalty) != 1 ||
        fscanf(file, "%d", write_allocate) != 1) {
        fprintf(stderr, "Error: Invalid config file format\n");
        fclose(file);
        exit(1);
    }

    fclose(file);
}

/**
 * @brief Processes a trace file and updates cache statistics.
 */
void process_trace(Cache *cache, const char *trace_filename, Stats *stats) {
    FILE *file = fopen(trace_filename, "r");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot open trace file %s\n", trace_filename);
        exit(1);
    }

    char access_type;
    uint32_t address;
    int instructions;

    while (fscanf(file, " %c %x %d", &access_type, &address, &instructions) == 3) {
        stats->total_cycles += instructions;

        stats->total_accesses++;
        if (access_type == 'l') {
            stats->load_accesses++;
        } else {
            stats->store_accesses++;
        }

        int hit = access_cache(cache, address, access_type, stats);

        if (hit) {
            stats->total_hits++;
            if (access_type == 'l') {
                stats->load_hits++;
            } else {
                stats->store_hits++;
            }
        }
    }

    stats->total_cycles += stats->total_mem_access_cycles;

    fclose(file);
}

/**
 * @brief Writes computed statistics to an output file.
 */
void write_output(const char *filename, Stats *stats) {
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot create output file %s\n", filename);
        exit(1);
    }

    double total_hit_rate = (stats->total_accesses > 0) ? 
        (100.0 * stats->total_hits / stats->total_accesses) : 0.0;
    
    double load_hit_rate = (stats->load_accesses > 0) ? 
        (100.0 * stats->load_hits / stats->load_accesses) : 0.0;
    
    double store_hit_rate = (stats->store_accesses > 0) ? 
        (100.0 * stats->store_hits / stats->store_accesses) : 0.0;
    
    double avg_mem_latency = (stats->total_accesses > 0) ? 
        ((double)stats->total_mem_access_cycles / stats->total_accesses) : 0.0;

    fprintf(file, "%.4f\n", total_hit_rate);
    fprintf(file, "%.4f\n", load_hit_rate);
    fprintf(file, "%.4f\n", store_hit_rate);
    fprintf(file, "%llu\n", (unsigned long long)stats->total_cycles);
    fprintf(file, "%.4f\n", avg_mem_latency);

    fclose(file);
}