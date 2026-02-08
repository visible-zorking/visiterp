/* Convert a 16-bit Z-machine packed address into its true address value.
   For Z-machine version 3, this just means doubling it. (If we
   ever support more versions, we'll need to do more work.)
*/
export function unpack_address(val: number) : number
{
    return val * 2;
}

/* Return a 16-bit Z-machine value as a signed integer. */
export function signed_zvalue(val: number) : number
{
    return (val < 32768) ? val : (val - 65536);
}

/* Given a file key, return the sourceloc of its first line. */
export function sourceloc_for_key(filekey: string) : string
{
    return filekey + ':1:1:1:0';
}

export type SourceLoc = {
    filekey: string;
    line: number;
    char: number;
    endline: number;
    endchar: number;
};

/* Parse a sourceloc string like "C:5:1" or "C:5:1:6:0" into its component
   parts. */
export function parse_sourceloc(val: string) : SourceLoc|undefined
{
    if (!val.length)
        return undefined;

    let tup = val.split(':');
    if (tup.length < 3)
        return undefined;

    let filekey = tup[0];
    let line = parseInt(tup[1]);
    let char = parseInt(tup[2]);
    
    if (tup.length < 5) {
        return {
            filekey: filekey,
            line: line,
            char: char,
            endline: line,
            endchar: 99999
        };
    }
    
    let endline = parseInt(tup[3]);
    let endchar = parseInt(tup[4]);
    
    if (endchar == 0) {
        endline -= 1;
        endchar = 99999;
    }
    
    return {
        filekey: filekey,
        line: line,
        char: char,
        endline: endline,
        endchar: endchar
    };
}
