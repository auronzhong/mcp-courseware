# MCP Server Specification: {Server Name}

**Server Name**: `mcp-server-{service-name}`
**Service**: {Service to integrate}
**Created**: {YYYY-MM-DD}
**Last Updated**: {YYYY-MM-DD}
**Status**: Draft | In Review | Approved | In Implementation | Completed
**Language**: Python (FastMCP) | TypeScript

---

## 1. Executive Summary

### 1.1 Server Overview
<!-- 2-3 句话描述这个 MCP Server 的目的和价值 -->

### 1.2 Target Service
**Service Name**: {service name}
**API Documentation**: {URL}
**Service Type**: {REST API, GraphQL, WebSocket, etc.}

### 1.3 Primary Use Cases
<!-- 用户会用这个 MCP Server 完成什么任务? -->
1. Use case 1
2. Use case 2
3. Use case 3

---

## 2. API Research Summary

<!-- 参考: .trae/specs/{server-name}/api-research.md -->

### 2.1 Authentication
**Method**: API Key | OAuth 2.0 | JWT | Basic Auth
**Required Scopes/Permissions**:
- scope1: description
- scope2: description

**Token Management**:
- How to obtain tokens
- Token expiration and refresh
- Storage recommendations

### 2.2 Rate Limits
**Limits**:
- Unauthenticated: {X} requests per hour
- Authenticated: {Y} requests per hour
- Concurrent requests: {Z}

**Headers**:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

**Handling Strategy**:
- Exponential backoff
- Request queuing
- Caching strategies

### 2.3 Key Endpoints
| Endpoint | Method | Purpose | Rate Limited |
|----------|--------|---------|--------------|
| `/endpoint1` | GET | Description | Yes/No |
| `/endpoint2` | POST | Description | Yes/No |

### 2.4 Data Models
<!-- 关键的数据结构 -->

**Model 1: {Name}**
```json
{
  "field1": "type",
  "field2": "type",
  "nested": {
    "field3": "type"
  }
}
```

**Model 2: {Name}**
```json
{
  "field1": "type"
}
```

### 2.5 Pagination
**Method**: Offset-based | Cursor-based | Page-based
**Parameters**:
- `page` or `cursor`: Pagination token
- `per_page` or `limit`: Items per page
- `max_results`: Maximum total results

**Response Format**:
```json
{
  "data": [...],
  "pagination": {
    "next": "cursor_token",
    "has_more": true
  }
}
```

### 2.6 Error Responses
| Status Code | Meaning | Example |
|-------------|---------|---------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | Internal error |

---

## 3. Tool Design

<!-- 参考: .trae/specs/{server-name}/tool-design.md -->

### 3.1 Tool Selection Rationale

#### Selected Tools (Priority Order)
1. **Tool 1**: {name}
   - **Value**: Why this tool is important
   - **Use Cases**: When users need it
   - **Complexity**: Simple | Medium | Complex

2. **Tool 2**: {name}
   - **Value**: Why this tool is important
   - **Use Cases**: When users need it
   - **Complexity**: Simple | Medium | Complex

#### Tools Not Implemented (and Why)
- **Endpoint X**: Reason for exclusion
- **Endpoint Y**: Reason for exclusion

### 3.2 Tool Workflow Design

#### Workflow 1: {Workflow Name}
**Goal**: {What users want to accomplish}
**Tools Involved**:
1. Tool A: {purpose in workflow}
2. Tool B: {purpose in workflow}
3. Tool C: {purpose in workflow}

**Example Scenario**:
```
User wants to: {specific task}
Steps:
1. Call tool_a(params) -> Get X
2. Use X to call tool_b(params) -> Get Y
3. Call tool_c(Y) -> Final result
```

---

## 4. Tool Specifications

### Tool 1: {tool_name}

#### 4.1.1 Overview
**Name**: `{tool_name}`
**Purpose**: {One-line description}
**Category**: Search | Content | Management | Analysis

**Detailed Description**:
{2-3 paragraphs explaining what this tool does, why it's valuable, and how it fits into workflows}

#### 4.1.2 Input Schema

```python
class ToolNameInput(BaseModel):
    model_config = {"extra": "forbid"}

    param1: str = Field(
        description="Description with examples",
        min_length=1,
        max_length=200,
        examples=["example1", "example2"]
    )

    param2: Optional[str] = Field(
        default=None,
        description="Optional parameter description"
    )

    format: Literal["json", "markdown"] = Field(
        default="json",
        description="Response format: 'json' for structured, 'markdown' for readable"
    )

    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="Detail level: 'concise' for summary, 'detailed' for full info"
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum results (1-100)"
    )
```

**Parameters Table**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| param1 | string | Yes | - | Description with examples |
| param2 | string | No | null | Optional description |
| format | enum | No | "json" | "json" or "markdown" |
| detail | enum | No | "concise" | "concise" or "detailed" |
| limit | integer | No | 10 | Max results (1-100) |

#### 4.1.3 Output Format

**Concise JSON Response**:
```json
[
  {
    "field1": "value",
    "field2": "value",
    "url": "https://..."
  }
]
```

**Detailed JSON Response**:
```json
[
  {
    "field1": "value",
    "field2": "value",
    "field3": "value",
    "nested": {
      "field4": "value"
    },
    "url": "https://..."
  }
]
```

**Concise Markdown Response**:
```markdown
**Item 1**: Summary
- Field: Value
- URL: https://...

**Item 2**: Summary
- Field: Value
- URL: https://...
```

**Detailed Markdown Response**:
```markdown
# Item 1

**Field1**: Value
**Field2**: Value

## Description
Detailed description...

[View Full Details](https://...)
```

#### 4.1.4 Tool Annotations

```python
annotations = {
    "readOnlyHint": True/False,     # This tool only reads data
    "destructiveHint": False/True,  # This tool doesn't modify/does modify data
    "idempotentHint": True/False,   # Repeated calls have same effect
    "openWorldHint": True           # Interacts with external system
}
```

#### 4.1.5 Error Handling

**Possible Errors**:
| Error | Cause | Agent Action |
|-------|-------|--------------|
| Authentication failed | Invalid/expired token | Check token configuration |
| Resource not found | Invalid ID/name | Verify parameter values |
| Rate limit exceeded | Too many requests | Wait and retry |
| Too many results | Query too broad | Narrow search with filters |

**Error Message Examples**:
```
Error: Repository 'user/repo' not found

Suggestion:
1. Check repository name format (should be: owner/repo)
2. Verify repository exists and is accessible
3. Ensure you have permission to access this repository

Example: search_repos(query="anthropics/claude")
```

#### 4.1.6 Usage Guidelines

**When to Use**:
- Scenario 1
- Scenario 2
- Scenario 3

**When NOT to Use**:
- Scenario 1 (use tool_x instead)
- Scenario 2 (use tool_y instead)

**Example Workflows**:
```
Workflow 1: {Name}
1. Call tool_name(param="value")
2. Process results
3. Use with other_tool() for next step

Workflow 2: {Name}
1. First use filter_tool() to narrow scope
2. Then call tool_name() with filtered params
```

---

### Tool 2: {tool_name}

<!-- Repeat structure for each tool -->

---

## 5. Shared Infrastructure Design

### 5.1 API Client

```python
class APIClient:
    """Shared API client for all tools"""

    def __init__(self, token: str, base_url: str):
        self.token = token
        self.base_url = base_url

    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict = None,
        data: dict = None,
        headers: dict = None
    ) -> dict:
        """
        Make authenticated API request

        Features:
        - Authentication header injection
        - Rate limit handling
        - Error response parsing
        - Retry with exponential backoff
        """
        pass

    async def paginate(
        self,
        endpoint: str,
        params: dict,
        max_pages: int = 10,
        max_results: int = 1000
    ) -> List[dict]:
        """Handle paginated API responses"""
        pass
```

### 5.2 Response Formatters

```python
class ResponseFormatter:
    """Format responses for different output modes"""

    @staticmethod
    def format_json(
        data: Any,
        detail: Literal["concise", "detailed"]
    ) -> str:
        """Format as JSON"""
        pass

    @staticmethod
    def format_markdown(
        data: Any,
        detail: Literal["concise", "detailed"]
    ) -> str:
        """Format as Markdown"""
        pass

    @staticmethod
    def truncate(text: str, max_tokens: int = 25000) -> str:
        """Truncate response to token limit"""
        pass
```

### 5.3 Error Handler

```python
class MCPError(Exception):
    """Base MCP error with actionable suggestions"""

    def __init__(self, message: str, suggestion: str = None):
        self.message = message
        self.suggestion = suggestion

def handle_api_error(error: Exception) -> MCPError:
    """Convert API errors to actionable MCP errors"""
    pass
```

---

## 6. Non-Functional Requirements

### 6.1 Performance

**Response Time Targets**:
- Simple queries: < 2 seconds
- Complex queries: < 10 seconds
- Bulk operations: < 30 seconds

**Character Limits**:
- Maximum response size: 25,000 tokens (~100,000 characters)
- Truncation strategy: Keep most important data, add truncation notice

**Caching Strategy**:
- Cache frequently accessed data
- Cache expiration: 5 minutes for dynamic data, 1 hour for static
- Cache invalidation on write operations

### 6.2 Reliability

**Error Recovery**:
- Automatic retry on transient errors (3 attempts)
- Exponential backoff: 1s, 2s, 4s
- Graceful degradation when possible

**Timeout Handling**:
- Request timeout: 30 seconds
- Overall operation timeout: 2 minutes

### 6.3 Scalability

**Concurrent Requests**:
- Support for multiple simultaneous tool calls
- Request queuing when rate limited
- Connection pooling for efficiency

**Large-Scale Data**:
- Pagination for large result sets
- Streaming for very large responses
- Batch processing where applicable

---

## 7. Security Considerations

### 7.1 Authentication Security

**Token Storage**:
- Never hardcode tokens
- Use environment variables
- Support secure token providers

**Token Validation**:
- Validate token format on startup
- Check token permissions
- Provide clear error messages for invalid tokens

### 7.2 Input Validation

**All Inputs Must Be Validated**:
- Use Pydantic/Zod schemas
- Enforce min/max lengths
- Validate formats (URLs, emails, etc.)
- Prevent injection attacks

### 7.3 Data Privacy

**Sensitive Data Handling**:
- Don't log tokens or credentials
- Sanitize error messages
- Follow service's data retention policies

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Test Coverage**:
- All API client functions
- All formatters
- All error handlers
- Each tool's input validation

**Mock API Responses**:
- Success scenarios
- Error scenarios
- Edge cases

### 8.2 Integration Tests

**Test Scenarios**:
- End-to-end tool execution
- Multi-tool workflows
- Error handling flows
- Rate limit handling

---

## 9. Evaluation Scenarios

<!-- 10 complex, realistic questions for testing -->

### 9.1 Evaluation Requirements

Each evaluation question must be:
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations
- **Complex**: Requiring multiple tool calls (3-5+)
- **Realistic**: Based on real use cases
- **Verifiable**: Single, clear answer
- **Stable**: Answer won't change over time

### 9.2 Example Evaluations

#### Evaluation 1
**Question**: {Complex question requiring deep exploration}
**Expected Answer**: {Single, verifiable answer}
**Tool Sequence**:
1. Call tool_a(params) to find X
2. Use X to call tool_b(params) to get Y
3. Filter Y and call tool_c(params)
4. Analyze results to find answer

#### Evaluation 2
**Question**: {Another complex question}
**Expected Answer**: {Single, verifiable answer}
**Tool Sequence**:
1. ...
2. ...

<!-- Total 10 evaluations -->

---

## 10. Implementation Plan

### 10.1 Phase 1: Foundation (Week 1)
- [ ] Set up project structure
- [ ] Implement API client
- [ ] Implement error handling
- [ ] Implement response formatters
- [ ] Write unit tests for infrastructure

### 10.2 Phase 2: Core Tools (Week 2-3)
- [ ] Implement Tool 1: {name}
- [ ] Implement Tool 2: {name}
- [ ] Implement Tool 3: {name}
- [ ] Write tests for each tool
- [ ] Create tool documentation

### 10.3 Phase 3: Advanced Tools (Week 4)
- [ ] Implement Tool 4: {name}
- [ ] Implement Tool 5: {name}
- [ ] Optimize performance
- [ ] Add caching

### 10.4 Phase 4: Testing & Documentation (Week 5)
- [ ] Create evaluation scenarios
- [ ] Run evaluations and iterate
- [ ] Write README and usage guide
- [ ] Create example workflows
- [ ] Final review and optimization

---

## 11. Open Questions

<!-- Track questions and clarifications -->

### Question 1: {Question}
**Asked by**: {Name}
**Asked on**: {Date}
**Context**: {Why this matters}
**Answer**: {To be determined}
**Answered by**: {Name}
**Answered on**: {Date}

---

## 12. References

### 12.1 Service Documentation
- API Documentation: {URL}
- Authentication Guide: {URL}
- Rate Limiting: {URL}

### 12.2 MCP Documentation
- MCP Protocol: https://modelcontextprotocol.io/llms-full.txt
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

### 12.3 Related Resources
- Resource 1: {Title, URL}
- Resource 2: {Title, URL}

---

## 13. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | {date} | {name} | Initial draft |
| 0.2 | {date} | {name} | Added tool designs |
| 1.0 | {date} | {name} | Approved for implementation |

---

## Appendix A: Complete Tool List

| Tool Name | Category | Priority | Status |
|-----------|----------|----------|--------|
| tool_1 | Search | High | Planned |
| tool_2 | Content | High | Planned |
| tool_3 | Management | Medium | Planned |
| tool_4 | Analysis | Low | Future |

## Appendix B: API Endpoints Mapping

| API Endpoint | MCP Tool | Notes |
|--------------|----------|-------|
| GET /api/v1/items | search_items | With filters |
| GET /api/v1/items/{id} | get_item | Single item |
| POST /api/v1/items | create_item | Future |
| DELETE /api/v1/items/{id} | delete_item | Future |

---

**Note**: This specification is a living document and should be updated as the implementation progresses and new requirements are discovered.
