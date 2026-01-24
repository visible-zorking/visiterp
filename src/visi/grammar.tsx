import React from 'react';
import { useState, useContext, createContext } from 'react';

import { GrammarLineData, GrammarClauseData, RoutineData, gamedat_grammar_lines, gamedat_grammar_verbnums, gamedat_grammar_line_addrs, gamedat_grammaractionlines, gamedat_actions, gamedat_routine_addrs, gamedat_attribute_names, gamedat_preposition_nums } from '../custom/gamedat';

import { ReactCtx } from './context';

export function GrammarTable()
{
    const [ sort, setSort ] = useState('alpha');
    
    let counter = 0;
    let lastverb = -1;
    let glinels = [];

    if (sort == 'alpha') {
        for (let gline of gamedat_grammar_lines) {
            let startgroup = false;
            if (gline.num != lastverb) {
                glinels.push(
                    <GrammarLineTail key={ counter } verbnum={ lastverb } />
                );
                counter++;
                
                lastverb = gline.num;
                startgroup = true;
            }
            glinels.push(
                <GrammarLine key={ counter } gline={ gline } startgroup={ startgroup } />
            );
            counter++;
        }
        glinels.push(
            <GrammarLineTail key={ counter } verbnum={ lastverb } />
        );
        counter++;
    }
    else {
        let lastaction = -1;
        for (let addr of gamedat_grammaractionlines) {
            let gline = gamedat_grammar_line_addrs.get(addr);
            if (gline) {
                let startgroup = false;
                if (lastaction != gline.action) {
                    startgroup = true;
                    lastaction = gline.action;
                }
                glinels.push(
                    <GrammarLine key={ counter } gline={ gline } startgroup={ startgroup } />
                );
                counter++;
            }
            //### GrammarLineTail?
        }
    }

    //### legend for loc flags
    //### dotted lines?
    
    function evhan_sort_change(val: string) {
        setSort(val);
    }
    
    return (
        <div className="ScrollContent">
            <div>
                Sort by{' '}
                <input id="sortalpha_radio" type="radio" name="sort" value="alpha" checked={ sort=='alpha' } onChange={ (ev) => evhan_sort_change('alpha') } />
                <label htmlFor="sortalpha_radio">Alpha</label>{' '}
                <input id="sortaction_radio" type="radio" name="sort" value="action" checked={ sort=='action' } onChange={ (ev) => evhan_sort_change('action') } />
                <label htmlFor="sortaction_radio">Action</label>
            </div>
            <ul className="DataList">
                { glinels }
            </ul>
        </div>
    );
}

function GrammarLineTail({ verbnum }: { verbnum: number })
{
    let verb = gamedat_grammar_verbnums.get(verbnum);
    if (!verb) {
        return null;
    }
    if (verb.words.length <= 1) {
        return null;
    }

    let ls = [];
    for (let ix=1; ix<verb.words.length; ix++) {
        let val = verb.words[ix];
        if (ix > 1) {
            ls.push(<span>, </span>);
        }
        ls.push(
            <span key={ ix } className="PrintDictWord">{ val }</span>
        );
    }

    return (
        <li className="GrammarLine">
            (... or { ls })
        </li>
    );
}

let prepcache: Map<number, JSX.Element> = new Map();

// Preposition display is completely static (based on gamedat_prepositions),
// so we memoize it.
function prep_element_full(val: number): JSX.Element
{
    let el = prepcache.get(val);
    if (el) 
        return el;

    let prep = gamedat_preposition_nums.get(val);
    let prepel: JSX.Element;
    if (prep) {
        if (!prep.syn) {
            prepel = (
                <>
                    {' '}
                    <span className="PrintDictWord">{ prep.text }</span>
                </>
            );
        }
        else {
            let ls = [ <span>{ prep.text }</span> ];
            for (let val of prep.syn) {
                ls.push(<span>/</span>);
                ls.push(<wbr/>);
                ls.push(<span>{ val }</span>);
            }
            prepel = (
                <>
                    {' '}
                    <span className="PrintDictWord">{ ls }</span>
                </>
            );
        }
    }
    else {
        prepel = (
            <>
                {' '}
                <span className="PrintDictWord">{ val }</span>
            </>
        );
    }

    prepcache.set(val, prepel);
    return prepel;
}

function GrammarClause({ clause }: { clause:GrammarClauseData })
{
    let rctx = useContext(ReactCtx);

    function evhan_click_attr(ev: React.MouseEvent<HTMLAnchorElement, MouseEvent>, index: number) {
        ev.preventDefault();
        rctx.setObjPage({ type:'ATTR', val:index });
    }
    
    let prepel: JSX.Element|null = null;
    let attrel: JSX.Element|null = null;
    let locel: JSX.Element|null = null;
    if (clause.prep) {
        prepel = prep_element_full(clause.prep);
    }
    if (clause.attr) {
        let attr = gamedat_attribute_names.get(clause.attr);
        if (attr) {
            attrel = (
                <>
                    <code>:<a className="Src_Id" href="#" onClick={ (ev) => evhan_click_attr(ev, attr.num) }>{ clause.attr }</a></code>
                </>
            );
        }
        else {
            attrel = (
                <>
                    <code>:{ clause.attr }</code>
                </>
            );
        }
    }
    if (clause.loc) {
        locel = (
            <>
                <code>:{ clause.loc }</code>
            </>
        );
    }
    let obj = (clause.count ? 'obj'+clause.count : 'obj');
    return (
        <span>
            { prepel } &nbsp;<span className="ClauseObj">{ obj }</span>{ locel }{ attrel }&nbsp;
        </span>
    );
}

function GrammarLine({ gline, startgroup }: { gline:GrammarLineData, startgroup?:boolean })
{
    let rctx = useContext(ReactCtx);

    let verb = gamedat_grammar_verbnums.get(gline.num);
    if (!verb) {
        return (<i>unknown verb: { gline.num }</i>);
    }
    
    let action = gamedat_actions[gline.action];

    function evhan_click_rtn(ev: React.MouseEvent<HTMLAnchorElement, MouseEvent>, func: RoutineData) {
        ev.preventDefault();
        rctx.setLoc(func.sourceloc, false);
    }

    let clausels = gline.clauses.map(clause => (
        <GrammarClause clause={ clause } />
    ));
    
    let funcel: JSX.Element|null = null;
    let prefuncel: JSX.Element|null = null;
    if (action.acrtn) {
        let func = gamedat_routine_addrs.get(action.acrtn);
        if (!func) {
            funcel = (
                <>
                    { (rctx.shownumbers ? <span className="ShowAddr">{ action.acrtn }:</span> : null) }
                    <i>???</i>
                </>
            );
        }
        else {
            funcel = (
                <>
                    { (rctx.shownumbers ? <span className="ShowAddr">{ action.acrtn }:</span> : null) }
                    <code><a className="Src_Id" href="#" onClick={ (ev) => evhan_click_rtn(ev, func) }>{ func.name }</a></code>
                </>
            );
        }
    }
    if (action.preacrtn) {
        let func = gamedat_routine_addrs.get(action.preacrtn);
        if (!func) {
            prefuncel = (
                <>
                    { (rctx.shownumbers ? <span className="ShowAddr">{ action.preacrtn }:</span> : null) }
                    <i>???</i>
                </>
            );
        }
        else {
            prefuncel = (
                <>
                    { (rctx.shownumbers ? <span className="ShowAddr">{ action.preacrtn }:</span> : null) }
                    <code><a className="Src_Id" href="#" onClick={ (ev) => evhan_click_rtn(ev, func) }>{ func.name }</a></code> /{' '}
                    { (rctx.shownumbers ? <br/> : null) }
                </>
            );
        }
    }

    let cla = (startgroup ? "GrammarLine StartGroup" : "GrammarLine");
    
    return (
        <li className={ cla }>
            <div className="GrammarLineAction">
                { prefuncel } { funcel }
            </div>
            <div className="GrammarLineDef">
                { (rctx.shownumbers ? <span className="ShowAddr">{ verb.num }:</span> : null) }
                <span className="PrintDictWord">{ verb.words[0] }</span>
                {' '}{ clausels }
            </div>
        </li>
    );
}
