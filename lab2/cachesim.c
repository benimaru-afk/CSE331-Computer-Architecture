/******************************************************************************
 *
 * filename: cachesim.c
 *
 * description: Implements a cache simulator.
 *
 * authors: Benjamin Mannal
 *
 * class: CSE 3031
 * instructor: Zheng
 * assignment: Lab #2
 *
 * assigned: 3/3/2026
 * due: 3/24/2026
 *
 ******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>

/* Cache line structure */
typedef struct {
    int valid;
    uint32_t tag;
    uint32_t fifo_order;  /* For FIFO replacement */
} CacheLine;

/* Cache set structure */
typedef struct {
    CacheLine *lines;
    uint32_t fifo_counter;
} CacheSet;

/* Cache structure */
typedef struct {
    CacheSet *sets;
    int num_sets;
    int associativity;
    int line_size;
    int replacement_policy;  /* 0 = random, 1 = FIFO */
    int miss_penalty;
    int write_allocate;      /* 0 = no-write-allocate, 1 = write-allocate */
} Cache;

/* Statistics structure */
typedef struct {
    uint64_t total_accesses;
    uint64_t total_hits;
    uint64_t load_accesses;
    uint64_t load_hits;
    uint64_t store_accesses;
    uint64_t store_hits;
    uint64_t total_cycles;
    uint64_t total_mem_access_cycles;  /* Cycles spent on memory accesses only */
} Stats;

/* Function prototypes */
Cache* create_cache(int line_size, int associativity, int data_size_kb, 
                    int replacement_policy, int miss_penalty, int write_allocate);
void free_cache(Cache *cache);
int access_cache(Cache *cache, uint32_t address, char access_type, Stats *stats);
void parse_config(const char *filename, int *line_size, int *associativity, 
                  int *data_size_kb, int *replacement_policy, 
                  int *miss_penalty, int *write_allocate);
void process_trace(Cache *cache, const char *trace_filename, Stats *stats);
void write_output(const char *filename, Stats *stats);
uint32_t get_set_index(Cache *cache, uint32_t address);
uint32_t get_tag(Cache *cache, uint32_t address);
int log2_int(int value);

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <config_file> <trace_file>\n", argv[0]);
        return 1;
    }

    /* Initialize random seed */
    srand(time(NULL));

    /* Parse configuration file */
    int line_size, associativity, data_size_kb;
    int replacement_policy, miss_penalty, write_allocate;
    
    parse_config(argv[1], &line_size, &associativity, &data_size_kb, 
                 &replacement_policy, &miss_penalty, &write_allocate);

    /* Create cache */
    Cache *cache = create_cache(line_size, associativity, data_size_kb, 
                                replacement_policy, miss_penalty, write_allocate);

    if (cache == NULL) {
        fprintf(stderr, "Error: Failed to create cache\n");
        return 1;
    }

    /* Initialize statistics */
    Stats stats = {0};

    /* Generate output filename */
    char output_filename[256];
    snprintf(output_filename, sizeof(output_filename), "%s.out", argv[2]);

    /* Process trace file */
    process_trace(cache, argv[2], &stats);

    /* Write output */
    write_output(output_filename, &stats);

    /* Cleanup */
    free_cache(cache);

    return 0;
}

/* Create and initialize cache */
Cache* create_cache(int line_size, int associativity, int data_size_kb, 
                    int replacement_policy, int miss_penalty, int write_allocate) {
    Cache *cache = (Cache *)malloc(sizeof(Cache));
    if (cache == NULL) return NULL;

    cache->line_size = line_size;
    cache->replacement_policy = replacement_policy;
    cache->miss_penalty = miss_penalty;
    cache->write_allocate = write_allocate;

    /* Calculate number of lines and sets */
    int total_data_size = data_size_kb * 1024;  /* Convert KB to bytes */
    int num_lines = total_data_size / line_size;

    if (associativity == 0) {
        /* Fully associative */
        cache->num_sets = 1;
        cache->associativity = num_lines;
    } else {
        cache->associativity = associativity;
        cache->num_sets = num_lines / associativity;
    }

    /* Allocate sets */
    cache->sets = (CacheSet *)malloc(cache->num_sets * sizeof(CacheSet));
    if (cache->sets == NULL) {
        free(cache);
        return NULL;
    }

    /* Allocate lines for each set */
    for (int i = 0; i < cache->num_sets; i++) {
        cache->sets[i].lines = (CacheLine *)calloc(cache->associativity, sizeof(CacheLine));
        cache->sets[i].fifo_counter = 0;
        if (cache->sets[i].lines == NULL) {
            /* Cleanup on failure */
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

/* Free cache memory */
void free_cache(Cache *cache) {
    if (cache == NULL) return;
    
    for (int i = 0; i < cache->num_sets; i++) {
        free(cache->sets[i].lines);
    }
    free(cache->sets);
    free(cache);
}

/* Calculate log base 2 of an integer */
int log2_int(int value) {
    int result = 0;
    while (value > 1) {
        value >>= 1;
        result++;
    }
    return result;
}

/* Get set index from address */
uint32_t get_set_index(Cache *cache, uint32_t address) {
    int offset_bits = log2_int(cache->line_size);
    int set_bits = log2_int(cache->num_sets);
    
    uint32_t set_index = (address >> offset_bits) & ((1 << set_bits) - 1);
    return set_index;
}

/* Get tag from address */
uint32_t get_tag(Cache *cache, uint32_t address) {
    int offset_bits = log2_int(cache->line_size);
    int set_bits = log2_int(cache->num_sets);
    
    uint32_t tag = address >> (offset_bits + set_bits);
    return tag;
}

/* Access cache and return 1 if hit, 0 if miss */
int access_cache(Cache *cache, uint32_t address, char access_type, Stats *stats) {
    uint32_t set_index = get_set_index(cache, address);
    uint32_t tag = get_tag(cache, address);
    
    CacheSet *set = &cache->sets[set_index];
    
    /* Check for hit */
    for (int i = 0; i < cache->associativity; i++) {
        if (set->lines[i].valid && set->lines[i].tag == tag) {
            /* Hit */
            stats->total_mem_access_cycles += 1;  /* Hit time is 1 cycle */
            return 1;
        }
    }
    
    /* Miss - need to handle based on write policy */
    if (access_type == 's' && cache->write_allocate == 0) {
        /* Store miss with no-write-allocate: don't bring into cache */
        stats->total_mem_access_cycles += 1 + cache->miss_penalty;
        return 0;
    }
    
    /* Miss - need to replace a line */
    int replace_index = -1;
    
    /* First check for invalid (empty) line */
    for (int i = 0; i < cache->associativity; i++) {
        if (!set->lines[i].valid) {
            replace_index = i;
            break;
        }
    }
    
    /* If no invalid line found, use replacement policy */
    if (replace_index == -1) {
        if (cache->replacement_policy == 0) {
            /* Random replacement */
            replace_index = rand() % cache->associativity;
        } else {
            /* FIFO replacement */
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
    
    /* Replace the line */
    set->lines[replace_index].valid = 1;
    set->lines[replace_index].tag = tag;
    set->lines[replace_index].fifo_order = set->fifo_counter++;
    
    stats->total_mem_access_cycles += 1 + cache->miss_penalty;
    return 0;  /* Miss */
}

/* Parse configuration file */
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

/* Process trace file */
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
        /* Add cycles for instructions executed since last memory access */
        stats->total_cycles += instructions;

        /* Update access counts */
        stats->total_accesses++;
        if (access_type == 'l') {
            stats->load_accesses++;
        } else {
            stats->store_accesses++;
        }

        /* Access cache (this will update total_mem_access_cycles) */
        int hit = access_cache(cache, address, access_type, stats);

        if (hit) {
            stats->total_hits++;
            if (access_type == 'l') {
                stats->load_hits++;
            } else {
                stats->store_hits++;
            }
        }
        
        /* Add memory access cycles to total cycles */
        /* Note: access_cache already added to total_mem_access_cycles */
    }
    
    /* Add the memory access cycles to total cycles */
    stats->total_cycles += stats->total_mem_access_cycles;

    fclose(file);
}

/* Write output statistics to file */
void write_output(const char *filename, Stats *stats) {
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot create output file %s\n", filename);
        exit(1);
    }

    /* Calculate hit rates */
    double total_hit_rate = (stats->total_accesses > 0) ? 
        (100.0 * stats->total_hits / stats->total_accesses) : 0.0;
    
    double load_hit_rate = (stats->load_accesses > 0) ? 
        (100.0 * stats->load_hits / stats->load_accesses) : 0.0;
    
    double store_hit_rate = (stats->store_accesses > 0) ? 
        (100.0 * stats->store_hits / stats->store_accesses) : 0.0;
    
    /* Calculate average memory access latency */
    /* This is total_mem_access_cycles / total_accesses */
    double avg_mem_latency = (stats->total_accesses > 0) ? 
        ((double)stats->total_mem_access_cycles / stats->total_accesses) : 0.0;

    /* Write statistics */
    fprintf(file, "%.4f\n", total_hit_rate);
    fprintf(file, "%.4f\n", load_hit_rate);
    fprintf(file, "%.4f\n", store_hit_rate);
    fprintf(file, "%llu\n", (unsigned long long)stats->total_cycles);
    fprintf(file, "%.4f\n", avg_mem_latency);

    fclose(file);
}
