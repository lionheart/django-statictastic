def combine_assets():
    pass

{% statictastic %}
<style type='text/css'>BLAH</style>
<style type='text/css' href=''>BLAH</style>
{% endstatictastic %}

==>

<style type='text/css' href='{% static "css/XYZ-1234567.css" %}' />

