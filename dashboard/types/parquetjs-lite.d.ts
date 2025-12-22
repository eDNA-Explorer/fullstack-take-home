declare module "parquetjs-lite" {
  export interface ParquetCursor {
    next(): Promise<Record<string, unknown> | null>;
  }

  export class ParquetReader {
    static openFile(filePath: string): Promise<ParquetReader>;
    getCursor(): ParquetCursor;
    close(): Promise<void>;
  }

  export class ParquetWriter {
    static openFile(
      schema: ParquetSchema,
      filePath: string
    ): Promise<ParquetWriter>;
    appendRow(row: Record<string, unknown>): Promise<void>;
    close(): Promise<void>;
  }

  export class ParquetSchema {
    constructor(schema: Record<string, SchemaDefinition>);
  }

  export interface SchemaDefinition {
    type: string;
    optional?: boolean;
    repeated?: boolean;
  }
}
