{%- extends 'full.tpl' -%}

{%- block any_cell -%}
{%- if 'jupyter:hide_cell' in cell.metadata.get("tags",[]) -%}
    <div class="hidden_cell">
    <input class="hide_cell" type="checkbox" checked></input>
        {{super() }}
    </div>
{%- elif 'jupyter:hide_output' in cell.metadata.get("tags",[]) and cell.cell_type == 'code'-%}
    <div class="hide_output_cell">
    <input class="hide_output" type="checkbox" checked></input>
        {{super() }}
    </div>
{%- elif 'jupyter:hide_input' in cell.metadata.get("tags",[]) and cell.cell_type == 'code'-%}
    <div class="hide_input_cell">
    <input class="hide_input" type="checkbox" checked></input>
        {{super() }}
    </div>
{%- else -%}
    {{ super() }}
{%- endif -%}
{%- endblock any_cell -%}


{%- block header -%}
{{ super() }}

<style type="text/css">

:root{
    --in-time: .5s;
    --out-time: .5s;
    --max-height-small: 0px;
    --max-height-big: 5000px;
    --transition-path-out: cubic-bezier(0, 0.67, 0.36, 1);
    --transition-path-in: ease-in-out;
    --padding-hidden: 0px;
}

div.hidden_cell > div.cell{
    transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -webkit-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -moz-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -o-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    max-height: var(--max-height-big);
}

div.hide_output_cell  div.output_wrapper{
    transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -webkit-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -moz-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -o-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    max-height: var(--max-height-big);
}

div.hide_input_cell  div.input{
    transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -webkit-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -moz-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    -o-transition: max-height var(--in-time) var(--transition-path-in), padding .0s step-end;
    max-height: var(--max-height-big);
}

div.hidden_cell, div.hide_output_cell, div.hide_input_cell{ display: flex; }

input[type=checkbox]{ align-self:center; }

input[type=checkbox].hide_cell:checked + div{
    overflow:hidden;
    max-height: var(--max-height-small);
    transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -webkit-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -moz-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -o-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    padding: var(--padding-hidden);
}

input[type=checkbox].hide_output:checked  + div div.output_wrapper{
    overflow:hidden;
    max-height: var(--max-height-small);
    transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -webkit-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -moz-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -o-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    padding: var(--padding-hidden);
}

input[type=checkbox].hide_input:checked  + div div.input{
    overflow:hidden;
    max-height: var(--max-height-small);
    transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -webkit-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -moz-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    -o-transition: max-height var(--out-time) var(--transition-path-out), padding var(--out-time) step-end;
    padding: var(--padding-hidden);
}

</style>
{%- endblock header -%}
