---
title: FastAPI v0.1.0
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 2

---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="fastapi">FastAPI v0.1.0</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

<h1 id="fastapi-default">Default</h1>

## chat_chat_docs_chat_post

<a id="opIdchat_chat_docs_chat_post"></a>

> Code samples

```shell
# You can also use wget
curl -X POST /chat-docs/chat \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json'

```

```http
POST /chat-docs/chat HTTP/1.1

Content-Type: application/json
Accept: application/json

```

```javascript
const inputBody = '{
  "knowledge_base_id": "string",
  "question": "string",
  "history": []
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json'
};

fetch('/chat-docs/chat',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Accept' => 'application/json'
}

result = RestClient.post '/chat-docs/chat',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

r = requests.post('/chat-docs/chat', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Accept' => 'application/json',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','/chat-docs/chat', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("/chat-docs/chat");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Accept": []string{"application/json"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "/chat-docs/chat", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /chat-docs/chat`

*Chat*

> Body parameter

```json
{
  "knowledge_base_id": "string",
  "question": "string",
  "history": []
}
```

<h3 id="chat_chat_docs_chat_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_chat_chat_docs_chat_post](#schemabody_chat_chat_docs_chat_post)|true|none|

> Example responses

> 200 Response

```json
{
  "question": "工伤保险如何办理？",
  "response": "根据已知信息，可以总结如下：\n\n1. 参保单位为员工缴纳工伤保险费，以保障员工在发生工伤时能够获得相应的待遇。\n2. 不同地区的工伤保险缴费规定可能有所不同，需要向当地社保部门咨询以了解具体的缴费标准和规定。\n3. 工伤从业人员及其近亲属需要申请工伤认定，确认享受的待遇资格，并按时缴纳工伤保险费。\n4. 工伤保险待遇包括工伤医疗、康复、辅助器具配置费用、伤残待遇、工亡待遇、一次性工亡补助金等。\n5. 工伤保险待遇领取资格认证包括长期待遇领取人员认证和一次性待遇领取人员认证。\n6. 工伤保险基金支付的待遇项目包括工伤医疗待遇、康复待遇、辅助器具配置费用、一次性工亡补助金、丧葬补助金等。",
  "history": [
    [
      "工伤保险是什么？",
      "工伤保险是指用人单位按照国家规定，为本单位的职工和用人单位的其他人员，缴纳工伤保险费，由保险机构按照国家规定的标准，给予工伤保险待遇的社会保险制度。"
    ]
  ],
  "source_documents": [
    "出处 [1] 广州市单位从业的特定人员参加工伤保险办事指引.docx：\n\n\t( 一)  从业单位  (组织)  按“自愿参保”原则，  为未建 立劳动关系的特定从业人员单项参加工伤保险 、缴纳工伤保 险费。",
    "出处 [2] ...",
    "出处 [3] ..."
  ]
}
```

<h3 id="chat_chat_docs_chat_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ChatMessage](#schemachatmessage)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## upload_file_chat_docs_upload_post

<a id="opIdupload_file_chat_docs_upload_post"></a>

> Code samples

```shell
# You can also use wget
curl -X POST /chat-docs/upload \
  -H 'Content-Type: multipart/form-data' \
  -H 'Accept: application/json'

```

```http
POST /chat-docs/upload HTTP/1.1

Content-Type: multipart/form-data
Accept: application/json

```

```javascript
const inputBody = '{
  "files": [
    "string"
  ],
  "knowledge_base_id": "string"
}';
const headers = {
  'Content-Type':'multipart/form-data',
  'Accept':'application/json'
};

fetch('/chat-docs/upload',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'multipart/form-data',
  'Accept' => 'application/json'
}

result = RestClient.post '/chat-docs/upload',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'multipart/form-data',
  'Accept': 'application/json'
}

r = requests.post('/chat-docs/upload', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'multipart/form-data',
    'Accept' => 'application/json',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','/chat-docs/upload', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("/chat-docs/upload");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"multipart/form-data"},
        "Accept": []string{"application/json"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "/chat-docs/upload", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /chat-docs/upload`

*Upload File*

> Body parameter

```yaml
files:
  - string
knowledge_base_id: string

```

<h3 id="upload_file_chat_docs_upload_post-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_upload_file_chat_docs_upload_post](#schemabody_upload_file_chat_docs_upload_post)|true|none|

> Example responses

> 200 Response

```json
{
  "code": 200,
  "msg": "success"
}
```

<h3 id="upload_file_chat_docs_upload_post-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[BaseResponse](#schemabaseresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## list_docs_chat_docs_list_get

<a id="opIdlist_docs_chat_docs_list_get"></a>

> Code samples

```shell
# You can also use wget
curl -X GET /chat-docs/list?knowledge_base_id=doc_id1 \
  -H 'Accept: application/json'

```

```http
GET /chat-docs/list?knowledge_base_id=doc_id1 HTTP/1.1

Accept: application/json

```

```javascript

const headers = {
  'Accept':'application/json'
};

fetch('/chat-docs/list?knowledge_base_id=doc_id1',
{
  method: 'GET',

  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Accept' => 'application/json'
}

result = RestClient.get '/chat-docs/list',
  params: {
  'knowledge_base_id' => 'string'
}, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('/chat-docs/list', params={
  'knowledge_base_id': 'doc_id1'
}, headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Accept' => 'application/json',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('GET','/chat-docs/list', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("/chat-docs/list?knowledge_base_id=doc_id1");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("GET");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Accept": []string{"application/json"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("GET", "/chat-docs/list", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`GET /chat-docs/list`

*List Docs*

<h3 id="list_docs_chat_docs_list_get-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|knowledge_base_id|query|string|true|Document ID|

> Example responses

> 200 Response

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    "doc1.docx",
    "doc2.pdf",
    "doc3.txt"
  ]
}
```

<h3 id="list_docs_chat_docs_list_get-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ListDocsResponse](#schemalistdocsresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## delete_docs_chat_docs_delete_delete

<a id="opIddelete_docs_chat_docs_delete_delete"></a>

> Code samples

```shell
# You can also use wget
curl -X DELETE /chat-docs/delete \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Accept: application/json'

```

```http
DELETE /chat-docs/delete HTTP/1.1

Content-Type: application/x-www-form-urlencoded
Accept: application/json

```

```javascript
const inputBody = '{
  "knowledge_base_id": "string",
  "doc_name": "string"
}';
const headers = {
  'Content-Type':'application/x-www-form-urlencoded',
  'Accept':'application/json'
};

fetch('/chat-docs/delete',
{
  method: 'DELETE',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/x-www-form-urlencoded',
  'Accept' => 'application/json'
}

result = RestClient.delete '/chat-docs/delete',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Accept': 'application/json'
}

r = requests.delete('/chat-docs/delete', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/x-www-form-urlencoded',
    'Accept' => 'application/json',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('DELETE','/chat-docs/delete', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("/chat-docs/delete");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("DELETE");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/x-www-form-urlencoded"},
        "Accept": []string{"application/json"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("DELETE", "/chat-docs/delete", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`DELETE /chat-docs/delete`

*Delete Docs*

> Body parameter

```yaml
knowledge_base_id: string
doc_name: string

```

<h3 id="delete_docs_chat_docs_delete_delete-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_delete_docs_chat_docs_delete_delete](#schemabody_delete_docs_chat_docs_delete_delete)|true|none|

> Example responses

> 200 Response

```json
{
  "code": 200,
  "msg": "success"
}
```

<h3 id="delete_docs_chat_docs_delete_delete-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[BaseResponse](#schemabaseresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

# Schemas

<h2 id="tocS_BaseResponse">BaseResponse</h2>
<!-- backwards compatibility -->
<a id="schemabaseresponse"></a>
<a id="schema_BaseResponse"></a>
<a id="tocSbaseresponse"></a>
<a id="tocsbaseresponse"></a>

```json
{
  "code": 200,
  "msg": "success"
}

```

BaseResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|code|integer|false|none|HTTP status code|
|msg|string|false|none|HTTP status message|

<h2 id="tocS_Body_chat_chat_docs_chat_post">Body_chat_chat_docs_chat_post</h2>
<!-- backwards compatibility -->
<a id="schemabody_chat_chat_docs_chat_post"></a>
<a id="schema_Body_chat_chat_docs_chat_post"></a>
<a id="tocSbody_chat_chat_docs_chat_post"></a>
<a id="tocsbody_chat_chat_docs_chat_post"></a>

```json
{
  "knowledge_base_id": "string",
  "question": "string",
  "history": []
}

```

Body_chat_chat_docs_chat_post

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|knowledge_base_id|string|true|none|Knowledge Base Name|
|question|string|true|none|Question|
|history|[array]|false|none|History of previous questions and answers|

<h2 id="tocS_Body_delete_docs_chat_docs_delete_delete">Body_delete_docs_chat_docs_delete_delete</h2>
<!-- backwards compatibility -->
<a id="schemabody_delete_docs_chat_docs_delete_delete"></a>
<a id="schema_Body_delete_docs_chat_docs_delete_delete"></a>
<a id="tocSbody_delete_docs_chat_docs_delete_delete"></a>
<a id="tocsbody_delete_docs_chat_docs_delete_delete"></a>

```json
{
  "knowledge_base_id": "string",
  "doc_name": "string"
}

```

Body_delete_docs_chat_docs_delete_delete

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|knowledge_base_id|string|true|none|Knowledge Base Name|
|doc_name|string|false|none|doc name|

<h2 id="tocS_Body_upload_file_chat_docs_upload_post">Body_upload_file_chat_docs_upload_post</h2>
<!-- backwards compatibility -->
<a id="schemabody_upload_file_chat_docs_upload_post"></a>
<a id="schema_Body_upload_file_chat_docs_upload_post"></a>
<a id="tocSbody_upload_file_chat_docs_upload_post"></a>
<a id="tocsbody_upload_file_chat_docs_upload_post"></a>

```json
{
  "files": [
    "string"
  ],
  "knowledge_base_id": "string"
}

```

Body_upload_file_chat_docs_upload_post

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|files|[string]|true|none|none|
|knowledge_base_id|string|true|none|Knowledge Base Name|

<h2 id="tocS_ChatMessage">ChatMessage</h2>
<!-- backwards compatibility -->
<a id="schemachatmessage"></a>
<a id="schema_ChatMessage"></a>
<a id="tocSchatmessage"></a>
<a id="tocschatmessage"></a>

```json
{
  "question": "工伤保险如何办理？",
  "response": "根据已知信息，可以总结如下：\n\n1. 参保单位为员工缴纳工伤保险费，以保障员工在发生工伤时能够获得相应的待遇。\n2. 不同地区的工伤保险缴费规定可能有所不同，需要向当地社保部门咨询以了解具体的缴费标准和规定。\n3. 工伤从业人员及其近亲属需要申请工伤认定，确认享受的待遇资格，并按时缴纳工伤保险费。\n4. 工伤保险待遇包括工伤医疗、康复、辅助器具配置费用、伤残待遇、工亡待遇、一次性工亡补助金等。\n5. 工伤保险待遇领取资格认证包括长期待遇领取人员认证和一次性待遇领取人员认证。\n6. 工伤保险基金支付的待遇项目包括工伤医疗待遇、康复待遇、辅助器具配置费用、一次性工亡补助金、丧葬补助金等。",
  "history": [
    [
      "工伤保险是什么？",
      "工伤保险是指用人单位按照国家规定，为本单位的职工和用人单位的其他人员，缴纳工伤保险费，由保险机构按照国家规定的标准，给予工伤保险待遇的社会保险制度。"
    ]
  ],
  "source_documents": [
    "出处 [1] 广州市单位从业的特定人员参加工伤保险办事指引.docx：\n\n\t( 一)  从业单位  (组织)  按“自愿参保”原则，  为未建 立劳动关系的特定从业人员单项参加工伤保险 、缴纳工伤保 险费。",
    "出处 [2] ...",
    "出处 [3] ..."
  ]
}

```

ChatMessage

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|question|string|true|none|Question text|
|response|string|true|none|Response text|
|history|[array]|true|none|History text|
|source_documents|[string]|true|none|List of source documents and their scores|

<h2 id="tocS_HTTPValidationError">HTTPValidationError</h2>
<!-- backwards compatibility -->
<a id="schemahttpvalidationerror"></a>
<a id="schema_HTTPValidationError"></a>
<a id="tocShttpvalidationerror"></a>
<a id="tocshttpvalidationerror"></a>

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|none|

<h2 id="tocS_ListDocsResponse">ListDocsResponse</h2>
<!-- backwards compatibility -->
<a id="schemalistdocsresponse"></a>
<a id="schema_ListDocsResponse"></a>
<a id="tocSlistdocsresponse"></a>
<a id="tocslistdocsresponse"></a>

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    "doc1.docx",
    "doc2.pdf",
    "doc3.txt"
  ]
}

```

ListDocsResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|code|integer|false|none|HTTP status code|
|msg|string|false|none|HTTP status message|
|data|[string]|true|none|List of document names|

<h2 id="tocS_ValidationError">ValidationError</h2>
<!-- backwards compatibility -->
<a id="schemavalidationerror"></a>
<a id="schema_ValidationError"></a>
<a id="tocSvalidationerror"></a>
<a id="tocsvalidationerror"></a>

```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|loc|[anyOf]|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|msg|string|true|none|none|
|type|string|true|none|none|

