{% macro log_transform(column, base=10, offset=0) %}
    {{ return(adapter.dispatch('log_transform', 'dbt_ml_inline_preprocessing')(column, base, offset)) }}
{% endmacro %}

{% macro default__log_transform(column, base, offset)  %}

    case
        when {{ column }} is null or {{ column }} + {{ offset }} <= 0 then null
        {% if base == 10 %}
            else log10({{ column }} + {{ offset }})
        {% elif base == 2 %}
            else log({{ column }} + {{ offset }}) / log(2)
        {% else %}
            else log({{ column }} + {{ offset }}) / log({{ base }})
        {% endif %}
    end

{% endmacro %}
