import React from 'react';

import { gamedat_object_ids, gamedat_string_map, gamedat_dictword_addrs, gamedat_actions, gamedat_property_nums, unpack_address } from '../custom/gamedat';
import { ObjPageLink } from './widgets';

export function VarShowObject({ value }: { value:number })
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

    return (<i>invalid object { value }</i>);
}

export function VarShowAction({ value }: { value:number })
{
    if (value >= 0 && value < gamedat_actions.length) {
        return (
            <>
                <span><code>{ gamedat_actions[value].name }</code></span>
            </>
        );
    }

    return (<i>invalid action { value }</i>);
}

export function VarShowProperty({ value }: { value:number })
{
    let prop = gamedat_property_nums.get(value);
    if (prop) {
        return (
            <span><code>P?{ prop.name }</code></span>
        );
    }

    if (value == 0) {
        return (<i>no property</i>);
    }

    return (<i>invalid property { value }</i>);
}

export function VarShowString({ value }: { value:number })
{
    let obj = gamedat_string_map.get(unpack_address(value));
    if (obj) {
        return (<span className="PrintString">&#x201C;{ obj.text }&#x201D;</span>);
    }

    return (<span>???</span>);
}

export function VarShowWord({ value }: { value:number })
{
    if (value == 0) {
        return <i>no word</i>;
    }
    
    let wd = gamedat_dictword_addrs.get(value);

    if (wd) {
        return (<span className="PrintDictWord">&#x2018;{ wd.text }&#x2019;</span>);
    }

    return (<i>invalid word { value }</i>);
}

