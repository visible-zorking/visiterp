import React from 'react';
import { useState, useContext, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

import { gamedat_ids, gamedat_global_names, gamedat_object_ids, sourceloc_start, find_sourceloc_for_id, sourceloc_for_srctoken } from '../custom/gamedat';

import { ZStatePlus, get_updated_report } from './zstate';
import { GnustoRunner, GnustoEngine } from './zstate';
import { sourceloc_for_first_text } from './zstate';
import { show_commentary } from './combuild';
import { CookiePrefs, set_cookie, set_body_ospref_theme, set_body_pref_theme, set_body_pref_arrange } from './cookie';

import { ContextContent, ReactCtx } from './context';
import { ObjPageFocus, SourceLocState, new_sourcelocstate } from './context';
import { AppMenu } from './menu';
import { SourceView } from './sourceview';

import { TabbedPane } from '../custom/tabs';

/* Hack alert: we're not running in Node.js here! But the rollup
   configuration replaces "process.env.NODE_ENV" with a static string,
   so we can check it. */
const releaseTarget = process.env.NODE_ENV;

let engine: GnustoEngine;
let initprefs: CookiePrefs;

export function set_app_context(enginev: GnustoEngine, initprefsv: CookiePrefs)
{
    engine = enginev;
    initprefs = initprefsv;
}

export function VisiZorkApp()
{
    let viewpaneref = useRefDiv();
    
    const [ zstate, setZState ] = useState(get_updated_report(engine));
    const [ tab, setTab ] = useState('activity');
    const [ objpage, setObjPage ] = useState(null as ObjPageFocus);
    const [ shownumbers, setShowNumbers ] = useState(initprefs.shownumbers);
    const [ readabout, setReadAbout ] = useState(initprefs.readabout);
    const [ arrangement, setArrangement ] = useState(initprefs.arrange);
    const [ theme, setTheme ] = useState(initprefs.theme);
    const [ sourcelocs, setSourceLocs ] = useState([ new_sourcelocstate() ]);
    const [ sourcelocpos, setSourceLocPos ] = useState(0);

    function setShowNumbersWrap(val: boolean) {
        set_cookie('shownumbers', (val ? 'true' : 'false'));
        setShowNumbers(val);
    }
    
    function setTabWrap(tab: string) {
        setTab(tab);
        setObjPage(null);
        if (tab == 'about') {
            set_cookie('readabout', 'true');
            setReadAbout(true);
        }
    }

    function setObjPageWrap(focus: ObjPageFocus) {
        setTab('objtree');
        setObjPage(focus);

        //### or prop, whatever
        if (focus && focus.type == 'OBJ') {
            let obj = gamedat_object_ids.get(focus.val);
            if (obj)
                rctx.setLoc(obj.sourceloc, false);
        }
    }
    
    function setLoc(loc: string, hi: boolean) {
        if (!loc)
            return;
        let ls = [ ...sourcelocs.slice(0, sourcelocpos+1), { loc:loc, lochi:hi } ];
        setSourceLocs(ls);
        setSourceLocPos(ls.length-1);
    }

    function shiftLoc(forward: boolean) {
        if (forward) {
            if (sourcelocpos < sourcelocs.length-1)
                setSourceLocPos(sourcelocpos+1);
        }
        else {
            if (sourcelocpos > 0)
                setSourceLocPos(sourcelocpos-1);
        }
    }

    useEffect(() => {
        function evhan_zstate(ev: Event) {
            let newstate = get_updated_report(engine);
            setZState(newstate);
            if (tab == 'activity') {
                let loc = sourceloc_for_first_text(newstate.calltree);
                if (loc)
                    setLoc(loc, true);
            }
            else if (tab == 'map') {
                let herenum = newstate.globals[0];
                let hereobj = gamedat_object_ids.get(herenum);
                if (hereobj) {
                    setLoc(hereobj.sourceloc, false);
                }
            }
        };
        window.addEventListener('zmachine-update', evhan_zstate);
        return () => {
            window.removeEventListener('zmachine-update', evhan_zstate);
        };
    }, [ tab ]);

    useEffect(() => {
        function evhan_sourceloc(ev: Event) {
            let detail = (ev as CustomEvent).detail;
            let sourceloc;
            if (detail.idtype == 'SRC')
                sourceloc = sourceloc_for_srctoken(detail.id);
            else
                sourceloc = find_sourceloc_for_id(detail.idtype, detail.id);
            if (!sourceloc) {
                console.log('BUG: sourceloc not found', detail);
                return;
            }
            setLoc(sourceloc, (detail.idtype == 'GLOB'));
        }
        window.addEventListener('zil-source-location', evhan_sourceloc);
        return () => {
            window.removeEventListener('zil-source-location', evhan_sourceloc);
        };
    }, [ sourcelocs, sourcelocpos ]);

    useEffect(() => {
        let resizer: ResizeObserver|undefined;
        let panesize = -1;
        if (viewpaneref.current) {
            resizer = new ResizeObserver((entries) => {
                if (entries.length) {
                    let newsize = entries[0].contentRect.width;
                    if (newsize < panesize-1 || newsize > panesize+1) {
                        panesize = newsize;
                        if (viewpaneref.current) {
                            if (panesize < 360)
                                viewpaneref.current.classList.add('Narrow');
                            else
                                viewpaneref.current.classList.remove('Narrow');
                        }
                    }
                }
            });
            resizer.observe(viewpaneref.current);
        }
        return () => {
            if (resizer)
                resizer.disconnect();
        };        
    }, []);

    useEffect(() => {
        let matcher = window.matchMedia('(prefers-color-scheme: dark)');
        set_body_ospref_theme(matcher.matches ? 'dark' : 'light');
        let callback = (ev: MediaQueryListEvent) => {
            set_body_ospref_theme(ev.matches ? 'dark' : 'light')
        };
        matcher.addEventListener('change', callback);
        return () => {
            matcher.removeEventListener('change', callback);
        };
    }, []);

    if (releaseTarget == 'development') {
        // In dev mode, we place some refs in global scope.
        (window as any).curzstate = zstate;
        (window as any).show_commentary = show_commentary;
    }

    let rctx: ContextContent = {
        zstate: zstate,
        tab: tab,
        objpage: objpage,
        sourcelocs: sourcelocs,
        sourcelocpos: sourcelocpos,
        shownumbers: shownumbers,
        readabout: readabout,
        theme: theme,
        arrangement: arrangement,
        setTab: setTabWrap,
        setObjPage: setObjPageWrap,
        setShowNumbers: setShowNumbersWrap,
        setLoc: setLoc,
        shiftLoc: shiftLoc,
        setTheme: setTheme,
        setArrangement: setArrangement,
        showCommentary: show_commentary,
    };

    let menuel = document.getElementById('appcontrols');
    
    return (
        <ReactCtx.Provider value={ rctx }>
            <div className="ViewPane" ref={ viewpaneref }>
                <TabbedPane />
            </div>
            <div className="SourcePane">
                <SourceView />
            </div>
            { menuel ? createPortal(<AppMenu />, menuel) : null }
        </ReactCtx.Provider>
    );
}

const useRefDiv = () => useRef<HTMLDivElement>(null);
