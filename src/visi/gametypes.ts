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

