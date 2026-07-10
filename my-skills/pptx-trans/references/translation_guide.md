# Translation Quality Guide

## Run Distribution Strategy

The core challenge of format-preserving translation is distributing translated text across existing runs while maintaining meaning and readability.

### Principle: Translate at Paragraph Level, Apply at Run Level

1. **Read** the `full_text` of the paragraph for complete context
2. **Translate** the entire paragraph as a unit
3. **Distribute** the translated text across the original runs

### Strategy by Paragraph Type

#### Single-Run Paragraphs (Most Common)

The simplest case — put the entire translation in the single run.

```
Original:  [Run0: "Cloud services are transforming the industry"]
Translate: [Run0: "클라우드 서비스가 산업을 혁신하고 있습니다"]
```

#### Multi-Run: Formatting Carries Meaning

When runs have different formatting, the formatting usually emphasizes specific terms. Preserve the association between formatting and key terms.

```
Original:
  Run0 (bold): "Amazon Bedrock"
  Run1 (normal): " provides foundation models for "
  Run2 (bold): "generative AI"
  Run3 (normal): " applications."

Translation:
  Run0 (bold): "Amazon Bedrock"           ← keep English (AWS service name)
  Run1 (normal): "은 "                     ← particle/connector
  Run2 (bold): "생성형 AI"                 ← preserve emphasis
  Run3 (normal): " 애플리케이션을 위한 파운데이션 모델을 제공합니다."
```

#### Multi-Run: Formatting is Cosmetic

Sometimes runs are split arbitrarily (e.g., due to editing history) with identical formatting. In this case, you can redistribute text more freely.

```
Original:
  Run0: "The service "    (no special formatting)
  Run1: "enables "        (no special formatting)
  Run2: "faster delivery" (no special formatting)

Translation:
  Run0: "이 서비스는 "
  Run1: "더 빠른 "
  Run2: "제공을 가능하게 합니다"
```

#### Empty or Whitespace Runs

Preserve runs that contain only spaces or are empty. They may serve as spacers.

```
Original: [Run0: "Title"] [Run1: "   "] [Run2: "Subtitle"]
Translate: [Run0: "제목"] [Run1: "   "] [Run2: "부제목"]
```

### Handling Uneven Distribution

Korean translations are often shorter or longer than the English original. The total character count may differ, but the number of runs must stay the same.

**When Korean is shorter**: Put extra space in the last run or distribute evenly.

**When Korean is longer**: This is normal. The text will still fit because PPTX text boxes auto-resize in most cases. If overflow is a concern, note it in the translation output.

## Technical Term Preservation

### Always Keep in English

| Category | Examples |
|----------|----------|
| AWS Services | Amazon S3, AWS Lambda, Amazon Bedrock, Amazon EC2, Amazon SageMaker, Amazon DynamoDB |
| AWS Concepts | Region, Availability Zone, VPC, IAM, CloudFormation |
| Product Names | Kubernetes, Docker, Terraform, GitHub, Jenkins |
| Acronyms | API, SDK, CI/CD, ML, AI, LLM, RAG, GenAI, IaC, SaaS, PaaS |
| Protocols | HTTP, HTTPS, REST, GraphQL, gRPC, WebSocket |
| Standards | JSON, YAML, XML, SQL, NoSQL |

### Translate to Korean

| Category | English | Korean |
|----------|---------|--------|
| Common IT terms | cloud | 클라우드 |
| | server | 서버 |
| | database | 데이터베이스 |
| | application | 애플리케이션 |
| | architecture | 아키텍처 |
| | security | 보안 |
| | monitoring | 모니터링 |
| | deployment | 배포 |
| | scalability | 확장성 |
| | availability | 가용성 |
| | latency | 지연 시간 |
| | throughput | 처리량 |
| | cost optimization | 비용 최적화 |
| | best practices | 모범 사례 |
| | use case | 사용 사례 |
| | workload | 워크로드 |

## Korean Writing Style for Presentations

### Formality Level

Use **합쇼체** (formal polite) for slide body text:
- "~합니다", "~됩니다", "~있습니다"
- NOT casual: "~해요", "~돼요"

Use **명사형 종결** (noun-ending) for bullet points and titles:
- "비용 절감" (cost reduction)
- "성능 향상" (performance improvement)

### Sentence Structure

Korean follows SOV (Subject-Object-Verb) order:
- English: "Amazon Bedrock provides foundation models"
- Korean: "Amazon Bedrock은 파운데이션 모델을 제공합니다"

### Particles and Connectors

Pay attention to Korean particles that connect to the previous word:
- 은/는 (topic marker): consonant ending → 은, vowel ending → 는
- 이/가 (subject marker): consonant → 이, vowel → 가
- 을/를 (object marker): consonant → 을, vowel → 를
- 와/과 (and): vowel → 와, consonant → 과

### Numbers and Units

- Keep Arabic numerals: 3개의 리전, 99.99% 가용성
- Keep English units when standard: 100ms, 1TB, 10Gbps

## Translation Output Format

When writing the translated JSON, add `translated_text` to each run:

```json
{
  "full_text": "Amazon Bedrock enables generative AI applications.",
  "runs": [
    {
      "index": 0,
      "text": "Amazon Bedrock",
      "translated_text": "Amazon Bedrock",
      "has_formatting": true
    },
    {
      "index": 1,
      "text": " enables generative AI applications.",
      "translated_text": "은 생성형 AI 애플리케이션을 가능하게 합니다.",
      "has_formatting": false
    }
  ]
}
```

The `apply_translation.py` script reads `translated_text` from each run and applies it via `run.text = translated_text`.
