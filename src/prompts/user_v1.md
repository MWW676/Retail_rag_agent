Please answer the following query based on the provided policies:

[QUERY START]
{{ query }}
[QUERY END]

[POLICIES START]
{% for c in chunks %}
[chunk_id: {{ c.chunk_id }}]
{{ c.text }}
{% if not loop.last %}

{% endif %}{% endfor %}
[POLICIES END]