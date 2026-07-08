# YOLO 조사 — 컴퓨터비전

> 출처: Evernote 노트 [컴퓨터비전 YOLO 조사](https://lite.evernote.com/note/76623b26-389b-4df6-9edb-15bc10421317) (2026-07-06 기록)
> vision 스포크의 얼굴 탐지 파인튜닝(`FaceTrainingInteractor`, `resources/yolo_train`)의 배경 지식 문서다.

## 요약

Object Detection(객체 검출) 분야의 역사와 방식을 보고, YOLO와 기존 방식의 차이점을 통해
향상된 기능을 이해한다. 아울러 계속 발전하는 객체 검출 방향을 예측해본다.

## 목차

1. [Object Detection(객체 검출)의 역사](#1-object-detection객체-검출의-역사)
2. [Object Detection(객체 검출)의 방식](#2-object-detection객체-검출의-방식)
3. [YOLO의 정의](#3-yolo의-정의)
4. [CNN계열 Fast R-CNN과 YOLO의 비교](#4-cnn계열-fast-r-cnn과-yolo의-비교)
5. [YOLO의 발전과정](#5-yolo의-발전과정)
6. [YOLO 조사결과와 의견](#6-yolo-조사결과와-의견)

---

## 1. Object Detection(객체 검출)의 역사

객체검출은 카메라나 다른 센서를 이용하여 자동차, 사람, 동물, 물건 등을 검출하는 것이다.
컴퓨팅파워가 좋아지기 전에는 이 문제는 모두 영상처리로 풀고 있다가, **2012년 AlexNet**이
나타나고부터는 딥러닝을 활용하여 문제를 접근하고 있다.

- 기존의 영상처리는 **정적인 상태**를 인식한다. 하나의 윈도에서 객체 검출을 위한 영역분할을
  하는데, 하나의 윈도우상에서 물체를 인식하는 것은 알고리즘의 성능이 좋지 않았다. 정지된
  객체의 인식과 대상 조작에 있어서 정확도가 많이 떨어졌다.
- 이를 해결하기 위해 **동적인 상태인식**을 통해 가상의 깊이 정보를 정의하도록 시도했고,
  이를 위해 **다계층 중첩 윈도우**를 적용한다. 다계층 중첩 윈도우 영역 간의 교차영역을
  지정하여 정확도를 올릴 수 있었다.
- 근래에는 밀집한 소형 물체의 정확한 위치 검출을 위한 다계층 중첩 윈도우를 이용한
  YOLO 네트워크의 성능개선이 이뤄지고 있다.

## 2. Object Detection(객체 검출)의 방식

딥러닝을 사용하는 객체검출 방식은 2가지가 있다.

### Two-shot detection (2단계 검출)

- ROI의 Window가 영상 전체를 Sliding 해가면서 계속 네트워크를 돌려준다. 한 장의 이미지에
  엄청나게 많은 여러 번의 네트워크를 사용해야 하므로 연산량이 엄청나게 많다.
  **거의 실시간성 zero**이다.
- 대표 신경망은 **R-CNN**이며 다음 프로세스로 작동한다:
  1. 예상범위 추출(RPN) — 대표적으로 Selective Search 알고리즘으로 추려낸다.
     비슷한 위치의 박스들을 줄여 **2000개의 랜덤사이즈 Bounding Box**만 남긴다.
  2. 이 모든 Bounding Box를 CNN으로 보낸다.
- 이 또한 몇 번의 네트워크를 통과해야 하므로 연산량이 꽤나 expensive하다.

### One-shot detection (1단계 검출)

- input image가 있으면 **하나의 신경망을 통과하여 물체의 bounding box와 class를 동시에
  예측**하는 방식이다.
- 대표적으로 **YOLO, SSD, RetinaNet** 등이 있다.

## 3. YOLO의 정의

- **You Only Look Once**의 약어. Joseph Redmon이 워싱턴 대학교에서 여러 친구들과 함께
  **2015년에 YOLOv1을 처음 논문과 함께 발표**했다.
- 당시만 해도 Object Detection에서는 대부분 Faster R-CNN(Region with Convolutional
  Neural Network)이 가장 좋은 성능을 내고 있었다.
- YOLO는 처음으로 One-shot detection 방법을 고안하였다. 이전까지 CNN 계열에서는
  Two-shot detection으로 Object Detection을 구성하였으나 실시간성이 굉장히 부족하다는
  단점이 있었다.

## 4. CNN계열 Fast R-CNN과 YOLO의 비교

| | Fast R-CNN | YOLO |
|---|---|---|
| 장점 | 높은 이미지 분류 정확도 | 합성곱 신경망을 **단 한 번** 통과 → 임의의 상품에 대해 피팅 가능 |
| 단점 | 과도한 오버헤드와 시간 소모 — 현실(실시간) 적용엔 무용 | 학습정도와 이미지 크기에 따라 모델 성능 저하 |

1. R-CNN → Fast R-CNN → Faster R-CNN → YOLO는 대략 **10배씩** 속도차이가 난다.
2. YOLO가 등장하여 **45프레임**을 보여주었고 빠른 버전의 경우 **155프레임**을 기록한다.
3. YOLO의 단점은 학습정도와 이미지 크기에 따라 모델의 성능이 크게 달라지며, **겹쳐있는
   상태에 대한 예측이 불확실**하다는 점이다.
4. 실생활 교통망에 적용하기에 위험요소가 있음을 인지하고, R-CNN 계열의 정확도를 수용한
   발전된 형태의 그리드 방식이 제안된다.

- 오류 분석(Fast R-CNN vs YOLO): Correct 71.6% vs 65.5%, Background 오검출 13.6% vs
  4.75%, Localization 오류 8.6% vs 19.0% — YOLO는 배경 오검출이 적은 대신 위치 오류가 크다.

## 5. YOLO의 발전과정

### YOLO v1
1. 네트워크 구조는 이미지 분류를 위해 설계된 **GoogleNet 모델 기반**
2. **24개의 콘볼루션 계층**과 **2개의 완전연결 계층**으로 구성
3. 풀링 계층은 사용 안 함

### YOLO v2
1. 대량의 분류 데이터를 활용하기 위해 고안된 방법
2. v1에 비해 정확도와 속도 향상을 위해 **일괄 정규화(Batch Normalization) 계층**을 추가
3. 경계 박스의 예측을 완전연결 계층 대신 **앵커박스**에서 수행하여 네트워크를 축소하면서
   출력 해상도를 향상

### YOLO v3
1. **로지스틱 회귀**를 적용하여 경계 박스의 객관성 점수(Objectness Score)를 예측
2. 경계 박스 예측, 클래스 예측, 특징 검출기 및 반복적 검출 방지를 개선
3. 결합된 특징 맵을 처리하고 보다 큰 텐서를 예측하기 위해 추가적인 콘볼루션 계층 포함

### YOLO v4
1. v3 이후에 나온 딥러닝의 정확도를 개선하는 다양한 방법을 적용해 성능을 극대화
2. 대표 모듈인 **SPP**는 딥러닝에 최적화하기 위해 CNN과 SPM을 결합하고 bag-of-words
   대신 maxpooling을 사용
3. 테스트 결과 v3 대비 추론시간 약 7% 증가, **정확도 5.7% 향상**

### YOLO v5
1. YOLOv3를 **PyTorch로 implementation**한 모듈이다
2. FPS와 mAP 측면에서 모두 뛰어난 성능 (FPS 140 / mAP 89.5)
3. 아키텍처에 CSPNet이 들어가는데 **BottleneckCSP**를 사용한다
4. 논문 "CSPNet: A New Backbone That Can Enhance Learning Capability of CNN" —
   CNN의 학습능력을 향상시킬 수 있는 새로운 백본으로 정의

## 6. YOLO 조사결과와 의견

- 최근 객체 검출 분야에서 딥러닝 알고리즘은 없어서는 안 되는 중요한 요소이다. 이들 중
  YOLO 네트워크는 딥러닝 네트워크의 단점인 **느린 처리속도를 획기적으로 줄임**으로써
  주목받고 있다.
- **데이터의 공급이 인공지능의 성능을 올리는 포커스**임은 분명하다. 이론에 머무르지 않고
  현실에 바로 적용 가능한 신경망 메소드를 통해 동적이미지 인식의 방법을 이해할 수 있었다.
- 하지만 YOLO 네트워크는 다른 딥러닝 알고리즘에 비해 **검출율이 비교적 낮다**는 단점을
  가지고 있다. 특히 **소형 오브젝트**에 대해서는 더욱 검출 성능이 낮아진다는 의견이 많다.
- 소형 물체의 높은 미검출이나 밀집된 상황에서의 오검출 같은 단점들을 개선하기 위해
  **다계층 중첩 윈도우 기반 알고리즘**으로 진화할 것으로 예측된다.

---

## 부록 — 보조 개념

### Feature Correlation

- 공간적 상관관계는 모든 특징 벡터의 곱을 계산하는 것으로 구성
  (예: `feature_A[k,:,i]`, `feature_B[k,:,j]`)
- 이를 위해 텐서의 차원 변형(상관관계 곱을 위하여)이 필요하다.

### Bilinear Interpolation

Example: A(2,1), B(7,4), E(4.9, 2.74)

1. 전체거리(d = B − A)를 구하고 시작점과 E 사이의 거리(d1 = E − A)도 구한다. 각각 5, 2.9.
2. d1 / d = 2.9 / 5 = 0.58 → 백분율로 58%. 즉 A로부터 B 방향으로 전체거리의 58%만큼
   움직이면 E가 나온다.
3. A와 B의 y 좌표 사이 거리에 위 배율을 곱한 뒤 A의 y 좌표를 더하면 E의 y 좌표를 구할 수
   있다. 답은 2.74.

### Segmentation 개념 (이해를 돕기 위한 기존 개념)

- Segmentation은 객체의 각 부위를 인식·탐지하고 그에 해당하는 label 값을 할당하는 것이다.
- 이를 통해 이미지의 각 부분을 의미론적 영역에서 구분한다.
- Human Parsing 계열(Self-Correction)의 구성: Online Model Aggregation ·
  Online Label Refinement · Get Loss
  1. loss = Parsing label(Human Parsing + Edge) − parsing branch + fusion branch
  2. loss = binary Edge − Edge prediction
  3. loss = 2 − 1
  4. loss = 1 + 2 + 3

## 주요 논문 출처 및 연구 논문 참고

1. 객체검출의 역사 — Object Detection in 20 Years: A Survey
   (<https://arxiv.org/pdf/1905.05055.pdf>)
2. Object Detection(객체 검출)의 방식 — <https://mickael-k.tistory.com/24?category=798521>
3. 밀집한 소형 물체의 정확한 위치 검출을 위한 다계층 중첩 윈도우를 이용한 YOLO 네트워크의
   성능개선 (유재형, 한영준, 한헌수)
4. 객체 검출을 위한 CNN과 YOLO 성능 비교 실험 (원광대학교 디지털콘텐츠공학과, 이용환, 김영섭)
5. VITON: An Image-based Virtual Try-on Network
6. Self-Correction for Human Parsing (Peike Li 외)
7. Devil in the Details: Towards Accurate Single and Multiple Human Parsing
