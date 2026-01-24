import React from 'react';

import { gamedat_property_nums, gamedat_string_map, gamedat_routine_addrs, gamedat_dictword_addrs, gamedat_object_ids, gamedat_actions, gamedat_preposition_nums, unpack_address, signed_zvalue, DictWordData, StringData } from '../custom/gamedat';

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
