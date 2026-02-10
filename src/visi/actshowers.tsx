import React from 'react';

import { signed_zvalue, unpack_address } from './gametypes';
import { gamedat_property_nums, gamedat_string_map, gamedat_routine_addrs, gamedat_dictword_addrs, gamedat_object_ids, gamedat_actions, gamedat_table_addrs, gamedat_preposition_nums, gamedat_grammar_verbnums, gamedat_grammar_line_addrs } from '../custom/gamedat';

import { ObjPageLink } from './widgets';

export function ArgShowObject({ value }: { value:number })
{
    if (value == 0)
        return (<i>nothing</i>);

    let obj = gamedat_object_ids.get(value);
    if (obj) {
        return (
            <>
                <ObjPageLink onum={ value } />
                <span><code>{ obj.name }</code></span>
            </>
        );
    }

    return (<i>?obj:{ value }</i>);
}

export function ArgShowRoutine({ value }: { value:number })
{
    if (value == 0)
        return (<i>false</i>);

    let func = gamedat_routine_addrs.get(unpack_address(value));
    if (func) {
        return (
            <span><code>{ func.name }</code></span>
        );
    }

    return (<i>?rtn:{ value }</i>);
}

export function ArgShowProperty({ value }: { value:number })
{
    let prop = gamedat_property_nums.get(value);
    if (prop) {
        return (
            <span><code>P?{ prop.name }</code></span>
        );
    }

    if (value == 0) {
        return (<i>no-prop</i>);
    }

    return (<i>?prop:{ value }</i>);
}

export function ArgShowString({ value }: { value:number })
{
    let obj = gamedat_string_map.get(unpack_address(value));
    if (obj) {
        let text = obj.text;
        if (text.length > 16)
            text = text.slice(0, 16)+'...';
        return (<span className="PrintString">&#x201C;{ text }&#x201D;</span>);
    }

    return (<span>???</span>);
}

export function ArgShowTable({ value }: { value:number })
{
    let tab = gamedat_table_addrs.get(value);
    if (tab) {
        return (
            <span>
                <code>,
                    { tab.name }
                    { tab.arrindex ? <i>[{ tab.arrindex }]</i> : null }
                </code>
            </span>
        );
    }

    return (<span> { signed_zvalue(value) }</span>);
}

export function ArgShowAction({ value }: { value:number })
{
    if (value >= 0 && value < gamedat_actions.length) {
        return (
            <>
                <span><code>{ gamedat_actions[value].name }</code></span>
            </>
        );
    }

    return (<i>?action:{ value }</i>);
}

export function ArgShowWord({ value }: { value:number })
{
    if (value == 0) {
        return <i>no word</i>;
    }
    
    let wd = gamedat_dictword_addrs.get(value);

    if (wd) {
        return (<span className="PrintDictWord">&#x2018;{ wd.text }&#x2019;</span>);
    }

    return (<i>?word{ value }</i>);
}

export function ArgShowPreposition({ value }: { value:number })
{
    if (value == 0) {
        return <i>no-prep</i>;
    }
    
    let prep = gamedat_preposition_nums.get(value);

    if (prep) {
        return (<span className="PrintDictWord">&#x2018;{ prep.text }&#x2019;</span>);
    }

    return (<i>?prep{ value }</i>);
}

export function ArgShowGrammarLine({ value }: { value:number })
{
    if (value == 0) {
        return <i>none</i>;
    }

    let gline = gamedat_grammar_line_addrs.get(value);

    if (gline) {
        let verb = gamedat_grammar_verbnums.get(gline.num);
        let verbwd = '???';
        if (verb?.words)
            verbwd = verb.words[0];
        let ls = [
            <span className="PrintDictWord">&#x2018;{ verbwd }</span>
        ];
        if (gline.clauses) {
            for (let clause of gline.clauses) {
                if (clause.prep) {
                    let prep = gamedat_preposition_nums.get(clause.prep);
                    if (prep) {
                        ls.push(
                            <>
                                {' '}<span className="PrintDictWord">{ prep.text }</span>
                            </>
                        );
                    }
                }
                ls.push(
                    <span className="PrintDictWord">...</span>
                );
                break;
            }
        }
        ls.push(
            <span className="PrintDictWord">&#x2019;</span>
        );

        return (
            <span>{ ls }</span>
        );
    }
    
    return (<i>?grammar{ value }</i>);
}

export function ArgShowMFlag({ value }: { value:number })
{
    /* Zork-specific -- see gmain.zil */
    let flag: string|null;

    switch (value) {
    case 1:
        return (<span><code>,M-BEG</code></span>);
    case 2:
        return (<span><code>,M-ENTER</code></span>);
    case 3:
        return (<span><code>,M-LOOK</code></span>);
    case 4:
        return (<span><code>,M-FLASH</code></span>);
    case 5:
        return (<span><code>,M-OBJDESC</code></span>);
    case 6:
        return (<span><code>,M-END</code></span>);
    default:
        return (<span> { signed_zvalue(value) }</span>);
    }
}
