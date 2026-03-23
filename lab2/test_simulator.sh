#!/bin/bash

###############################################################################
# test_simulator.sh
# 
# Comprehensive testing script for cache simulator
# Tests compilation, execution, and output validation
# CSE 3031 - Lab 2
###############################################################################

echo "=========================================="
echo "Cache Simulator Test Suite"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Check if source file exists
echo -n "Test 1: Source file exists... "
if [ -f "cachesim.c" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "  Error: cachesim.c not found"
    ((TESTS_FAILED++))
fi

# Test 2: Check if Makefile exists
echo -n "Test 2: Makefile exists... "
if [ -f "Makefile" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "  Error: Makefile not found"
    ((TESTS_FAILED++))
fi

# Test 3: Compilation test
echo -n "Test 3: Compilation... "
make clean > /dev/null 2>&1
if make > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "  Error: Compilation failed"
    ((TESTS_FAILED++))
fi

# Test 4: Executable created
echo -n "Test 4: Executable created... "
if [ -f "cachesim" ] && [ -x "cachesim" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "  Error: cachesim executable not found or not executable"
    ((TESTS_FAILED++))
fi

# Test 5: Check for config directory
echo -n "Test 5: Config directory exists... "
if [ -d "confs" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}WARN${NC}"
    echo "  Warning: confs/ directory not found"
    echo "  Create it and add config files from Canvas"
fi

# Test 6: Check for trace directory
echo -n "Test 6: Trace directory exists... "
if [ -d "traces" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}WARN${NC}"
    echo "  Warning: traces/ directory not found"
    echo "  Create it and add trace files from Canvas"
fi

# Test 7: Create test configuration
echo -n "Test 7: Creating test configuration... "
mkdir -p test_temp
cat > test_temp/test.conf << EOF
8
1
16
1
100
1
EOF
if [ -f "test_temp/test.conf" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((TESTS_FAILED++))
fi

# Test 8: Create test trace
echo -n "Test 8: Creating test trace... "
cat > test_temp/test.trace << EOF
l 0x1000 5
s 0x2000 3
l 0x1000 2
s 0x3000 4
l 0x2000 1
EOF
if [ -f "test_temp/test.trace" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((TESTS_FAILED++))
fi

# Test 9: Run simulator with test data
echo -n "Test 9: Running simulator... "
if [ -f "cachesim" ]; then
    if ./cachesim test_temp/test.conf test_temp/test.trace > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Error: Simulator execution failed"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}SKIP${NC} (no executable)"
fi

# Test 10: Check output file created
echo -n "Test 10: Output file created... "
if [ -f "test_temp/test.trace.out" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    echo "  Error: Output file not created"
    ((TESTS_FAILED++))
fi

# Test 11: Validate output format
echo -n "Test 11: Output format validation... "
if [ -f "test_temp/test.trace.out" ]; then
    line_count=$(wc -l < test_temp/test.trace.out)
    if [ "$line_count" -eq 5 ]; then
        echo -e "${GREEN}PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Error: Expected 5 lines, found $line_count"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}SKIP${NC} (no output file)"
fi

# Test 12: Check hit rate range
echo -n "Test 12: Hit rate validation... "
if [ -f "test_temp/test.trace.out" ]; then
    hit_rate=$(head -1 test_temp/test.trace.out)
    if (( $(echo "$hit_rate >= 0" | bc -l) )) && (( $(echo "$hit_rate <= 100" | bc -l) )); then
        echo -e "${GREEN}PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Error: Hit rate $hit_rate is out of range [0, 100]"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}SKIP${NC} (no output file)"
fi

# Test 13: Test with fully associative cache
echo -n "Test 13: Fully associative cache... "
cat > test_temp/fullassoc.conf << EOF
8
0
16
0
100
1
EOF
if ./cachesim test_temp/fullassoc.conf test_temp/test.trace > /dev/null 2>&1; then
    if [ -f "test_temp/test.trace.out" ]; then
        echo -e "${GREEN}PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}FAIL${NC}"
    echo "  Error: Fully associative cache test failed"
    ((TESTS_FAILED++))
fi

# Test 14: Test with different replacement policy
echo -n "Test 14: Random replacement policy... "
cat > test_temp/random.conf << EOF
8
2
16
0
100
1
EOF
if ./cachesim test_temp/random.conf test_temp/test.trace > /dev/null 2>&1; then
    if [ -f "test_temp/test.trace.out" ]; then
        echo -e "${GREEN}PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}FAIL${NC}"
    echo "  Error: Random replacement test failed"
    ((TESTS_FAILED++))
fi

# Test 15: Source code header check
echo -n "Test 15: Source code header... "
if grep -q "filename: cachesim.c" cachesim.c && \
   grep -q "CSE 3031" cachesim.c && \
   grep -q "Lab #2" cachesim.c; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}WARN${NC}"
    echo "  Warning: Check that source header is properly filled out"
fi

# Cleanup
rm -rf test_temp

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Add configuration files to confs/ directory"
    echo "2. Add trace files to traces/ directory"
    echo "3. Run: ./run_all_simulations.sh"
    echo "4. Generate graphs: python3 analyze_results.py"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "Please fix the errors before proceeding."
    exit 1
fi
