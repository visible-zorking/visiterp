import React from 'react';
import { useContext } from 'react';

import { gamedat_ids, gamedat_object_ids, gamedat_routine_names } from '../visi/gamedat';
import { ZObject } from '../visi/zstate';

import { ReactCtx } from '../visi/context';
import { ObjPageLink, Commentary } from '../visi/widgets';

export function AboutPage()
{
    let rctx = useContext(ReactCtx);
    let zstate = rctx.zstate;

    let lastupdate = '__VISIZORKDATE__';
        
    let curroom = '???';
    let firstobj = '';

    let map: Map<number, ZObject> = new Map();
    for (let tup of zstate.objects) {
        map.set(tup.onum, tup);
    }
    
    let advroom: number = gamedat_ids.ADVENTURER;
    while (true) {
        let tup = map.get(advroom);
        if (!tup || tup.parent == 0 || tup.parent == gamedat_ids.ROOMS)
            break;
        advroom = tup.parent;
    }

    if (advroom != gamedat_ids.ADVENTURER) {
        let obj = gamedat_object_ids.get(advroom);
        if (obj) {
            curroom = obj.name;
        }

        let child = map.get(advroom)!.child;
        if (child && child == gamedat_ids.ADVENTURER) {
            child = map.get(child)!.sibling;
        }

        if (child) {
            let cobj = gamedat_object_ids.get(child);
            if (cobj) {
                firstobj = cobj.desc.toUpperCase();
            }
        }
        else if (obj && obj.scenery && obj.scenery.length) {
            let cobj = gamedat_object_ids.get(obj.scenery[0]);
            if (cobj) {
                firstobj = cobj.desc.toUpperCase();
            }
        }
    }
    
    function evhan_click_tab(ev: React.MouseEvent<HTMLAnchorElement, MouseEvent>, tab: string) {
        ev.preventDefault();
        rctx.setTab(tab);
    }
    
    function evhan_click_routine(ev: React.MouseEvent<HTMLAnchorElement, MouseEvent>, rtn: string) {
        ev.preventDefault();
        let funcdat = gamedat_routine_names.get(rtn);
        if (funcdat) {
            rctx.setLoc(funcdat.sourceloc, false);
        }
    }
    
    return (
        <div className="ScrollContent">
            <div className="AboutPage">
                <h2>What&#x2019;s going on?</h2>
                <p>
                    You are playing <i>TITLE</i>, the classic Infocom text adventure.
                    And you are watching the Z-machine execute the game,
                    live, as you play.
                </p>
                <p>
                    (In case it&#x2019;s not obvious: <em>SPOILERS</em> for <i>TITLE</i>.
                    The source code gives away every secret and solution in the game.
                    The whole point of this project is to demonstrate how
                    Infocom games work!)
                </p>
                <p>
                    Type commands in the left pane. (If you&#x2019;re not familiar
                    with parser games,{' '}
                    <ExtWebLink url={ 'https://pr-if.org/doc/play-if-card/' } text={ 'here\u2019s a quick intro' } />.)
                    As the game responds, the panes on the right will display
                    the current game state and the code that is
                    executing.
                </p>
                <p>
                    Look at the
                    {' '}<a className="Internal" href="#" onClick={ (ev)=>evhan_click_tab(ev, 'objtree') }>World</a>{' '}
                    tab for a start.
                    This shows every object and room in the game.
                    You, the Adventurer, are in the topmost room:{' '}
                    <code>{ curroom }</code>.
                    Listed with you are the objects you
                    can see.{' '}
                    { (firstobj ?
                       <>(Try typing &#x201C;<code>EXAMINE { firstobj }</code>&#x201D;!) </>
                       : null) }
                    Objects you pick up will be listed directly under
                    the <code>ADVENTURER</code>; they will move with
                    you as part of your inventory.
                </p>
                <p>
                    The other tabs display other aspects of the Z-machine.
                    {' '}<a className="Internal" href="#" onClick={ (ev)=>evhan_click_tab(ev, 'activity') }>Activity</a>{' '}
                    shows the functions called in
                    the most recent turn, and what they printed.
                    {' '}<a className="Internal" href="#" onClick={ (ev)=>evhan_click_tab(ev, 'globals') }>State</a>{' '}
                    shows all the game&#x2019;s global variables.
                    {' '}<a className="Internal" href="#" onClick={ (ev)=>evhan_click_tab(ev, 'timers') }>Timers</a>{' '}
                    shows the table of timed events.
                    {' '}<a className="Internal" href="#" onClick={ (ev)=>evhan_click_tab(ev, 'grammar') }>Grammar</a>{' '}
                    shows the parse table.
                    {' '}<a className="Internal" href="#" onClick={ (ev)=>evhan_click_tab(ev, 'map') }>Map</a>{' '}
                    is what you think.                    
                </p>
                <p>
                    Click on any function, object, or variable to see its
                    definition in the source code. Click on an object&#x2019;s
                    {' '}<ObjPageLink onum={ gamedat_ids.ADVENTURER } /> button
                    to see its current state and place in the world.
                    (This will initially match the source code, but
                    may change as you interact with the game.)
                </p>
                <p>
                    <Commentary topic={ 'ABOUT' } />
                    Click on the green buttons to see commentary about{' '}
                    <i>TITLE</i>&#x2019;s implementation. Notes, trivia, whatever came
                    into my head as I was building the Visible Zorker!
                </p>
                <h2>The FEELIES</h2>
                <p>
                    The <a className="Internal" href="#" onClick={ (ev)=>evhan_click_tab(ev, 'feelies') }>Feelies</a>{' '}
                    tab is particularly important. <i>TITLE</i> originally
                    came with ###.... The Feelies tab
                    contains links to these documents, as well as other
                    commands you will need to play.
                </p>
                <h2>About this release</h2>
                <p>
                    <i>TITLE</i> was originally released in XXXX.
                    The version you see here dates from XXXX. (The serial number
                    &#x201C;XXXXXX&#x201D; shows the compile date.)
                    As with Zork, it was built using a proprietary system
                    called{' '}
                    <ExtWebLink url={ 'https://blog.zarfhome.com/2019/04/what-is-zil-anyway' } text={ 'ZIL' } />.
                    (For &#x201C;Zork Implementation Language&#x201D;.)
                </p>
                <p>
                    This is the first known version, released in 1982.
                    (The serial number
                    &#x201C;820901&#x201D; shows the compile date.)
                    A slightly later release (&#x201C;821021&#x201D;)
                    was included in the &#x201C;
                    <ExtWebLink url={ 'https://archive.org/details/lost-treasures-of-infocom' } text={ 'Lost Treasures of Infocom' } />
                    &#x201D; collection and later collections.
                    However, we do not have the source code for that
                    release, so I selected the original for this exhibit.
                    Archived evidence indicates that Infocom continued
                    updating the source through XXXX.
                </p>
                <h2>Sources and acknowledgements</h2>
                <p>
                    The game&#x2019;s source code was first{' '}
                    <ExtWebLink url={ 'https://github.com/historicalsource/TITLE' } text={ 'publicly released' } />
                    {' '}by Jason Scott in April 2019.
                    I then combed through all known versions and posted my{' '}
                    <ExtWebLink url={ 'https://eblong.com/infocom/' } text={ 'Obsessively Complete Infocom Catalog' } />,
                    which now includes this Visible Zorker exhibition.
                </p>
                <p>
                    The Visible Zorker is built on a seriously customized
                    version of the{' '}
                    <ExtWebLink url={ 'https://github.com/curiousdannii/parchment' } text={ 'Parchment' } /> Z-machine interpreter
                    by Marnanel Thurman, Atul Varma, and Dannii Willis.
                    You can find this, and the rest of the Visible Zorker
                    machinery, on{' '}
                    <ExtWebLink url={ 'https://github.com/visible-zorking/visi-zork3' } text={ 'Github' } />.
                </p>
                <p>
                    I used TXD from the{' '}
                    <ExtWebLink url={ 'https://ifarchive.org/indexes/if-archive/infocom/tools/ztools/' } text={ 'ZTools' } />
                    {' '}package to analyze the game file. That
                    process was invaluably aided by the{' '}
                    <ExtWebLink url={ 'https://ifarchive.org/indexes/if-archive/infocom/tools/reform/' } text={ 'Infocom analysis work' } />
                    {' '}done in 2007 by Allen Garvin, Ben Rudiak-Gould,
                    and Ethan Dicks.
                </p>
                <p>
                    The fonts used are Courier Prime, Lato, and
                    Libre Baskerville. The header background is copied from
                    Infocom&#x2019;s Zork hint maps.
                </p>
                <p>
                    Feelie scans courtesy of the{' '}
                    <ExtWebLink url={ 'https://infodoc.plover.net/manuals/' } text={ 'InfoDoc Project' } />
                    {' '}and my own collection.
                    See also the{' '}
                    <ExtWebLink url={ 'https://archive.org/details/XXXX' } text={ 'Internet Archive' } />.
                </p>
                <p>
                    <i>TITLE</i> itself was originally written by XXXX.
                    It is copyright 1983 (etc) by Infocom,
                    then Activision, then renamed to Mediagenic,
                    then Bobby Kotick bought it and renamed it Activision,
                    then Vivendi bought it and merged it with Blizzard,
                    then Microsoft consumed the lot.
                </p>
                <p>
                    Thus, the <i>TITLE</i> source code is copyright 2025 by
                    Microsoft. Microsoft has not released this game as
                    open source, but I&#x2019;m going at it regardless.
                </p>
                <p>
                    Aside from the above, the Visible Zorker is copyright
                    2025-2026 by Andrew Plotkin. MIT license;{' '}
                    <ExtWebLink url={ 'https://github.com/visible-zorking/visi-starcross' } text={ 'Github repo' } />.
                </p>
                <h2>Patreon supporters</h2>
                <ul className="PatreonList">
                    <li>
                        <b>Fancy contributors:</b>{' '}
                        <NameList level="Fancy Contributor" />
                    </li>
                    <li>
                        <b>Contributors:</b>{' '}
                        <NameList level="Contributor" />
                    </li>
                    <li className="Small">
                        <b>Participants:</b>{' '}
                        <NameList level="Participant" />
                    </li>
                    <li className="Smaller">
                        <b>Supporters:</b>{' '}
                        <NameList level="Supporter" />
                    </li>
                </ul>
                <hr/>
                <p>
                    Last updated <b>{ lastupdate }</b>.
                    This exhibit is hosted by the{' '}
                    <ExtWebLink url={ 'https://eblong.com/infocom/' } text={ 'Obsessively Complete Infocom Catalog' } />.
                </p>
            </div>
        </div>
    );
}

export function ExtWebLink({ url, text }: { url:string, text:string })
{
    return (
        <a className="External" target="_blank" href={ url }>{ text }</a>
    );
}

function NameList({ level }: { level:string })
{
    let names = patreon_donors[level];

    if (!names || names.length == 0) {
        return <></>;
    }

    let text = names.join(', ');
    return <span>{ text }</span>;
}

const patreon_donors: { [key: string]: string[] } = {
    "Contributor": ["Ben Cressey", "Brad Jones", "Christopher Cotton", "Jeff Nyman", "John Leen", "Matthew Murray", "Paul Mazaitis", "Peter Berger", "Yoon Ha Lee"],
    "Fancy Contributor": ["David Rheingold"],
    "Participant": ["Aaron Reed", "Adam B", "Adam Thornton", "Alex Seubert", "Allyson Gray", "Anders Madsen", "Andy Baio", "Aneel Nazareth", "arcanetrivia", "chad royal", "Chris Spiegel", "Christian N", "Curtis Frye", "Damien Neil", "Daniel Sharpe", "David Cornelson", "DJ Lang", "Doug Orleans", "Emily Short", "Eric Nyman", "Georg Wille", "Henrik \u00c5sman", "J. Ryan Stinnett", "James Tranovich", "Jason Compton", "Jo Walton", "John Faulkenbury", "John Krewson", "Josh Johnson", "Joshua Grams", "JT", "Jules Graybill", "Liza Daly", "Mark Musante", "Mark Sample", "Marty McGuire", "Matthew Blakley", "Matthew Griffin", "Michael Rubin", "Mike Wiese", "Monica M", "ndiddy", "Olivier L.", "Patrick Palmer", "pdxeric", "Roody Yogurt", "Tobias V. Langhoff", "Torbj\u00f6rn Andersson", "Y. K. Lee", "Zeke Pabski"],
    "Supporter": ["Cat", "Christopher", "Daniel Smith", "Derrell Piper", "Eric Neustadter", "Lachlan Cooper", "louis rodriguez", "Nevin", "Vivienne Dunstan"],
}
