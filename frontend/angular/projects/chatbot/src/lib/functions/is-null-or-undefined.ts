export function isNullOrUndefined(_value: any): _value is undefined {
    return _value === null || _value === undefined;
}