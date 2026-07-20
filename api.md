# [API] 멀티모달 위험 평가 통합 챗봇 API

## 1. Base URL

```bash
https://141.223.163.135:3457
https://141.223.163.135:8000
```

---

## 2 Functions

### GET `/`

- **설명**: 클라이언트가 서비스의 루트 URL(`/`)로 접근하면 메인 상담 페이지 `index.html`을 반환합니다.
- **Response**: HTML

### Post `/chat/chat1`

- 사용자의 발화, 이미지(선택)을 입력으로 받아 다음 챗봇의 발화를 생성합니다.
- score: 사용자의 점수를 key:value 형태로 string으로 반환

**Request (Body-JSON)**

```jsx
{
	"sender_id": "test@example.com",
	"text":"안녕하세요. 요즘 기분에 대해 이야기하고 싶어요.", 
	"image":""
	}
```

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `sender_id` | string | 사용자 식별 ID (이메일) |
| `text` | string | 사용자 입력 메시지 |
| `image` | data:image/png;base64,<base64 데이터> | 이미지 데이터 또는 이미지 URL/base64 문자열 (`""`이면 이미지 없음 |

**Response**

```jsx
{
    "text": [
        "4일 동안 우울한 기분을 느끼셨군요. 그 기간 동안 어떤 일이 있으셨는지 좀 더 구체적으로 이야기해 주실 수 있을까요?"
    ],
    "score": "4: 0, 6: 2",
    "is_ending": false
}
```

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `text` | array[string] | 챗봇 응답 메시지 리스트 |
| `score` | string | 문항별 평가 점수 (`문항번호: 점수` 형식) |
| `is_ending` | boolean | 대화 종료 여부 (`true`면 종료) |

### Example cURL Test **(/chat/chat1)**

- 이미지(사용자 얼굴)가 있다면 base64 encoding, 없다면 “”

```jsx
curl -k -X POST "https://141.223.163.135:3457/chat/chat1"   
-H "Content-Type: application/json"   
-d "{
		\"sender_id\":\"curl_test_user\",
		\"text\":\"안녕하세요. 요즘 기분에 대해 이야기하고 싶어요\",
		\"image\":\"\"
		}"
```

### GET `/tts`

- 발화(텍스트)를 입력으로 받아 오디오를 출력합니다.
- **https 버전입니다.**

**Request**

text = “안녕하세요.”

**Response**: 오디오

% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
Dload  Upload   Total   Spent    Left  Speed
100 65578    0 65578    0     0  25479      0 --:--:--  0:00:02 --:--:-- 25477

### Example cURL Test (/tts)

```jsx
curl -k --get --data-urlencode "text=안녕하세요" "https://141.223.163.135:3457/tts" --output out.mp3
```

- 파일 저장 없는 버전

```jsx
curl -k --get --data-urlencode "text=안녕하세요" "https://141.223.163.135:3457/tts" 
```

### Post `/speech-to-text`

- **https 버전입니다.**
- 음성 파일을 입력으로 받아 텍스트를 반환한다.
- 음성파일 포맷: audio/webm, audio/wav, audio/mp3, audio/ogg

**Request (.js)**

```jsx
const blob = new Blob(audioChunks, { type: "audio/webm" });

const fd = new FormData();
fd.append("file", blob, "speech.webm");

await fetch("/speech-to-text", {
  method: "POST",
  body: fd
});
```

**Response**

```jsx
{"transcript":"안녕하세요."}
```

### Example cURL Test (/speech-to-text)

- type에 가능한 형식: audio/webm, audio/wav, audio/mpeg, audio/ogg

```jsx
curl -k -X POST "https://141.223.163.135:3457/speech-to-text" \
  -F "file=@out.mp3;type=audio/mpeg"
```

### GET `/send_recent_logs`

- is_ending = True일 때 호출 (chat/chat1의 response)

### Request

```jsx
import requests

url = "https://141.223.163.135:8000/send_recent_logs?user_id=curl_test_user"

payload = ""
headers = {
  'Authorization': 'Bearer df0cbd2879f829ec97580f15b988f67150805e2ede12210c435bfcfb389285b2'
}

response = requests.request("GET", url, headers=headers, data=payload)
```

### Response

- 아래의 Logging 형식과 같음. ([4. Logging (Server side)](https://app.notion.com/p/4-Logging-Server-side-2b77c6d8512b80b5a295f1a867dddb7a?pvs=21))

### cURL Test(/send_recent_logs)

- Bearer를 꼭 넣어서 호출
- Bearer df0cbd2879f829ec97580f15b988f67150805e2ede12210c435bfcfb389285b2

```jsx
curl -k -X GET \
  -H "Authorization: Bearer df0cbd2879f829ec97580f15b988f67150805e2ede12210c435bfcfb389285b2" \
  "https://141.223.163.135:8000/send_recent_logs?user_id=default_user"

```

---

## UNIST API

- 챗봇 소견 페이지를 위한 API
- 8001번 포트 사용

### 요약 생성 `POST /generate_summary?user_id={user_id}`

- 상담 완료 시 (`is_ending = True`), `main.py`에서 **자동으로 호출**함.

제공 앱:

- `unist.py`
- 기본 포트 `8001`

동작:

1. `logs/{user_id}/`에서 최신 상담 로그를 찾는다.
2. `history`와 `score`를 prompt에 삽입한다.
3. `gpt-4o-mini`를 호출해 구조화된 JSON 요약을 생성한다.
4. `logs/{user_id}/{timestamp}_{user_id}_summary.json`에 저장한다.

Response 예시:

```json
{
  "status": "done",
  "summary_file": "logs/user-001/2026-06-11_15-00-00_user-001_summary.json"
}
```

### 요약 상태 조회 `GET /summary_status?user_id={user_id}`

제공 앱:

- `unist.py`
- 기본 포트 `8001`

용도:

- 특정 사용자의 상담 요약 파일 생성 여부를 polling하기 위한 엔드포인트이다.
- `logs/{user_id}/`에서 `_{user_id}_summary.json` 패턴의 파일을 찾고, 파일명 정렬 기준 가장 마지막 파일을 최신 summary로 간주한다.

Query parameter:

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `user_id` | string | yes | 상태를 조회할 사용자 ID |

가능한 response body:

| 상황 | HTTP status | Response body | 설명 |
| --- | --- | --- | --- |
| 사용자 로그 디렉터리가 없음 | 200 | `{"status": "not_started"}` | `logs/{user_id}` 경로가 아직 생성되지 않은 상태 |
| 요약 파일이 없음 | 200 | `{"status": "not_started"}` | 사용자 로그 디렉터리는 있지만 `*_{user_id}_summary.json` 파일이 없는 상태 |
| 최신 요약 파일을 읽을 수 없음 | 200 | `{"status": "error"}` | JSON 파일 열기 또는 parsing 중 예외가 발생한 상태 |
| 최신 요약 파일에 `status` 필드가 있음 | 200 | `{"status": "{파일의 status}", "summary_file": "{파일명}"}` | 일반적으로 `/generate_summary`가 만든 파일이면 `done` 반환 |
| 최신 요약 파일에 `status` 필드가 없음 | 200 | `{"status": "unknown", "summary_file": "{파일명}"}` | summary 파일은 있으나 상태 필드가 없는 비정상 또는 수동 생성 파일 |

호출 예시:

```bash
curl -X GET "http://141.223.163.135:8001/summary_status?user_id=user-001"
```

정상 완료 예시:

```json
{
  "status": "done",
  "summary_file": "2026-06-11_15-00-00_user-001_summary.json"
}
```

아직 요약이 시작되지 않은 경우:

```json
{
  "status": "not_started"
}
```

요약 파일은 있으나 읽기 실패한 경우:

```json
{
  "status": "error"
}
```

요약 파일은 있으나 내부 `status` 값이 없는 경우:

```json
{
  "status": "unknown",
  "summary_file": "2026-06-11_15-00-00_user-001_summary.json"
}
```

참고:

- `/generate_summary`가 정상적으로 완료되면 summary 파일 내부 `status`는 `"done"`으로 저장된다.
- `/generate_summary` 호출 자체가 실패하면 별도 summary 파일이 생성되지 않으므로, 이후 `/summary_status`는 보통 `"not_started"`를 반환한다.
- 이 엔드포인트는 요약 본문을 반환하지 않는다. 요약 내용은 `/get_summary`에서 조회한다.

### 요약 결과 조회 `GET /get_summary?user_id={user_id}`

- /summary_status의 return 값이 “done”일 때 호출
- 챗봇 소견 항목을 받을 수 있는 API
- 제공 앱:
    - `unist.py`
    - 기본 포트 `8001`

호출 예시:

```bash
curl -X GET "http://141.223.163.135:8001/get_summary?user_id=yang0617_3"
```

Response 예시:

```json
{
  "status": "done",
  "summary": {
    "keywords": [
      {
        "type": "증상",
        "content": "슬픔으로 가득 찬 날들"
      },
      {
        "type": "솔루션",
        "content": "새로운 시작을 위한 첫걸음"
      }
    ],
    "key1": "상사에게 혼났다는 사건에서 경찰관님은 큰 슬픔을 느끼셨던 것 같습니다. 그로 인해 자신의 가치에 대한 의구심까지 드셨다고 이야기하셨죠. 현재는 힘든 감정들이 가득해 보이지만, 이러한 감정들은 인간이면 누구나 겪을 수 있는 것들이거든요. 특히 다른 사람에게 피해를 준다는 우려는 많은 사람들이 겪는 감정인데, 이를 통해 경찰관님의 공감능력이 얼마나 큰지를 보여주고 있어요.",
    "key2": "혹시 말씀하신 '다른 분들을 피해를 보게 할까 걱정된다'는 마음을 잠시 내려놓고, 단순히 매일 10분 정도 자신에게 집중하는 시간을 가져보는 건 어떨까요? 이렇게 스스로를 돌아보는 시간을 가지면 스트레스가 완화되고, 심박수를 안정시켜 교감신경의 흥분을 가라앉힐 수 있어요. 이후에 더욱 맑은 마음으로 업무에 임할 수 있게 될 것입니다.",
    "key3": "최근 계속 늘어나는 상사의 압박 속에서 느끼는 **심리적 피로**를 풀어줄 콘텐츠가 아래에 준비되어 있습니다. 이러한 자료들을 통해 지금의 힘든 기분을 조금이나마 덜 수 있길 바라요, 경찰관님."
  },
  "created_at": "2026-06-17T14:02:12.727037",
  "updated_at": "2026-06-17T14:02:12.727037",
  "summary_file": "logs/yang0617_3/2026-06-17_14-00-00_yang0617_3.json"
}
```

## 3. Session Management

- 사용자는 `sender_id`를 통해 식별됩니다.
- 각 상담 세션은 `sender_id`와 상담 시작 시각을 기준으로 식별됩니다.
- 사용자가 “is_ending”: False인 상태에서 24시간 안에 재접속 시 상담을 이어서 진행할 수 있습니다.

## 4. Logging (Server side)

- 매 턴의 대화 기록은 `/logs/{sender_id}/{date_time}_{sender_id}.json`에 누적 저장됩니다.
- 상담 진행 상태와 문항별 CES-D 점수는 별도의 `/logs/{sender_id}/state_{sender_id}_{date_time}.json` 파일에 저장됩니다.
- 대화 로그 형식은 아래와 같습니다.

```json
{
  "history": [
    {
      "speaker": "User",
      "text": "요즘 근무가 좀 힘들어서요. 그냥 누군가랑 이야기하고 싶다는 생각이 들었어요.",
      "time": "2025-10-15T19:41:30.136316"
    },
    {
      "speaker": "Bot",
      "text": "그렇군요. 그런 기분이 드실 때, 어떤 방식으로 스트레스를 해소하시나요?",
      "time": "2025-10-15T19:41:30.136316"
    },
    {
      "speaker": "User",
      "text": "잠을 잘 못 자서 더 지치는 것 같아요.",
      "time": "2025-10-15T19:43:02.421107"
    },
    {
      "speaker": "Bot",
      "text": "잠들기 어렵거나 자주 깨시는 편인가요?",
      "time": "2025-10-15T19:43:02.421107"
    }
  ]
}

