# Python 문법 정리

## 리스트와 딕셔너리

Python에서 자주 사용되는 자료구조입니다.

### 리스트 (List)

순서가 있는 데이터의 모음입니다.

```python
fruits = ["사과", "바나나", "오렌지"]
fruits.append("포도") # 추가fruits.pop() # 마지막 요소 제거
```

### 딕셔너리 (Dictionary)

```
키-값 쌍으로 데이터를 저장합니다.```

python

person = {

"name": "홍길동",

"age": 25,

"city": "서울"

}

```
## 클래스와 객체지향```

`객체지향 프로그래밍의 기본 단위입니다.`

python

class Dog:

```
    def __init__(self, name):```

`        self.name = name    def bark(self):        print(f"{self.name}가 짖습니다!")my_dog = Dog("멍멍이")my_dog.bark()`

## `파일 입출력`

`파일을 읽고 쓰는 방법입니다.`

python

# 파일 쓰기

```
with open("data.txt", "w") as f:```

`    f.write("Hello, World!")`

# `파일 읽기`

`with open("data.txt", "r") as f:    content = f.read()`

## `예외 처리`

`오류를 안전하게 처리하는 방법입니다.`python

try:`

`    result = 10 / 0`

`except ZeroDivisionError:`

`    print("0으로 나눌 수 없습니다!")`

`finally:`

`    print("처리 완료")`