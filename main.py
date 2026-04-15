import json
import time

# [제약 사항] 허용 오차 설정
EPSILON = 1e-9

# [기능 요구 사항] 표준 라벨 정의
LABEL_CROSS = "Cross"
LABEL_X = "X"
LABEL_UNDECIDED = "UNDECIDED"

def normalize_label(raw_label):
    raw_label = str(raw_label).lower().strip()
    if raw_label in ['+', 'cross']:
        return LABEL_CROSS
    elif raw_label == 'x':
        return LABEL_X
    return raw_label

def get_matrix_input(size, name):
    matrix = []
    print(f"{name} ({size}줄 입력, 공백 구분)")
    row = 0
    while row < size:
        try:
            line = input().split()
            if len(line) != size:
                print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
                continue
            numeric_row = [float(x) for x in line]
            matrix.append(numeric_row)
            row += 1
        except ValueError:
            print("숫자 파싱 실패: 숫자만 입력 가능합니다. 다시 입력해주세요.")
    return matrix

def calculate_mac(pattern, filter_matrix):
    score = 0.0
    size = len(pattern)
    for r in range(size):
        for c in range(size):
            score += pattern[r][c] * filter_matrix[r][c]
    return score

def judge_pattern(score_a, score_b):
    if abs(score_a - score_b) < EPSILON:
        return LABEL_UNDECIDED
    return LABEL_CROSS if score_a > score_b else LABEL_X

def measure_performance(pattern, filter_a, filter_b, iterations=10):
    start_time = time.perf_counter()
    for _ in range(iterations):
        _ = calculate_mac(pattern, filter_a)
        _ = calculate_mac(pattern, filter_b)
    end_time = time.perf_counter()
    return ((end_time - start_time) * 1000) / iterations

def print_summary(summary):
    print("\n#-------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#-------")
    print(" 크기    평균 시간(ms)    연산 횟수(N^2)")
    print("-------------------------------------")
    for n in [3, 5, 13, 25]:
        dummy_p = [[0.0]*n for _ in range(n)]
        dummy_f = [[0.0]*n for _ in range(n)]
        avg_t = measure_performance(dummy_p, dummy_f, dummy_f, 10)
        print(f" {n}x{n:<4} {avg_t:>10.6f} ms {n*n:>10}")

    print("\n#-------")
    print("# [4] 결과 요약")
    print("#-------")
    print(f"총 테스트: {summary['total']}개")
    print(f"통과: {summary['pass']}개")
    print(f"실패: {summary['fail']}개")
    for case in summary['failed_cases']:
        print(case)

def run_mode_1():
    print("\n# [1] 필터 입력")
    filter_a = get_matrix_input(3, "필터 A")
    filter_b = get_matrix_input(3, "필터 B")
    print("\n# [2] 패턴 입력")
    pattern = get_matrix_input(3, "패턴")
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    avg_time = measure_performance(pattern, filter_a, filter_b)
    print(f"\nA 점수: {score_a}\nB 점수: {score_b}\n시간: {avg_time:.6f} ms\n판정: {judge_pattern(score_a, score_b)}")

def run_mode_2():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("에러: data.json 파일을 찾을 수 없습니다.")
        return

    print("\n# [1] 필터 로드")
    filters = data.get("filters", {})
    for size_key in filters:
        print(f"✓ {size_key} 필터 로드 완료 (Cross, X)")

    print("\n# [2] 패턴 분석")
    patterns = data.get("patterns", {})
    results_summary = {"total": 0, "pass": 0, "fail": 0, "failed_cases": []}

    for p_key, p_value in patterns.items():
        try:
            size_n = int(p_key.split('_')[1])
            f_set = filters.get(f"size_{size_n}")
            input_p = p_value.get("input")
            expected_norm = normalize_label(p_value.get("expected"))
            
            s_cross = calculate_mac(input_p, f_set.get("cross"))
            s_x = calculate_mac(input_p, f_set.get("x"))
            prediction = judge_pattern(s_cross, s_x)

            results_summary["total"] += 1
            if prediction == expected_norm:
                results_summary["pass"] += 1
                status = "PASS"
            else:
                results_summary["fail"] += 1
                status = "FAIL"
                results_summary["failed_cases"].append(f"- {p_key}: 불일치")
            
            print(f"{p_key} | {prediction} | expected: {expected_norm} | {status}")
        except Exception as e:
            print(f"Error at {p_key}: {e}")
            
    print_summary(results_summary)

def main():
    while True:
        print("\n=== Mini NPU Simulator ===")
        print("1. 사용자 입력 | 2. JSON 분석 | 0. 종료")
        choice = input("선택: ")
        if choice == '1': run_mode_1()
        elif choice == '2': run_mode_2()
        elif choice == '0': break

if __name__ == "__main__":
    main()
