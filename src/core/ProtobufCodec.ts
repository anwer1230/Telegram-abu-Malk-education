/**
 * ProtobufCodec.ts - Serialization Utilities for Protocol Buffers
 */

export namespace GoogleProtobuf {
  export interface Timestamp {
    seconds: number;
    nanos: number;
  }

  export function encodeTimestamp(date: Date = new Date()): Timestamp {
    return {
      seconds: Math.floor(date.getTime() / 1000),
      nanos: (date.getTime() % 1000) * 1000000,
    };
  }
}
