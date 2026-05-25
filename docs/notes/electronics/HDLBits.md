# 一些HDLBits上的题目

##### lemming 1:

```verilog
module top_module(
    input clk,
    input [7:0] in,
    input reset,    // Synchronous reset
    output done); //
    
    reg [1:0] state;	//0-none 1-bit1ok! 2-byte2 3-byte3(in this stage we set done)
    parameter byte1 = 2'b00, byte2 = 2'b01, byte3 = 2'b10, doned = 2'b11;
    
    // State transition logic (combinational)
    
    // State flip-flops (sequential)
    always@(posedge clk)	// the byte input only when we encounter a posedge
        begin
            if(reset == 1) begin
                state <= byte1;
            end
            case (state)
            byte1:
                if(in[3] == 1)
                    state <= byte2;
            byte2: state <= byte3;
            byte3: state <= doned;
            doned:
                if(in[3] == 1)
                    state <= byte2;
                else
                    state <= byte1;
            endcase
        end
    // Output logic
    assign done = (state == doned);
endmodule
```



##### fsm serial

我的题解：

```verilog
module top_module(
    input clk,
    input in,
    input reset,    // Synchronous reset
    output done
); 
    parameter IDLE=4'b0001, DATA=4'b0010, STOP=4'b0100, ERR=4'b1000;
    reg [3:0] state;
    reg [3:0] next_state;
    reg [2:0] cnt;
    reg STOP2IDLE;
    wire STOPPED;
    assign STOPPED = in & (state == STOP);
    // transitional logic
    always@(*) begin
        case (state)
            IDLE:next_state = in ? IDLE : DATA;
            DATA:next_state = (cnt == 3'd7) ? STOP : DATA;
            STOP:next_state = in ? IDLE : ERR;
            ERR:next_state = in ? IDLE : ERR;		// until it finds stop bit (1)     
            default: next_state = state;
        endcase
    end
    always@(posedge clk) begin
        if(reset) begin
           state <= IDLE;
           cnt <= 3'b0;
            STOP2IDLE <= 1'b0;
        end
        else begin
           state <= next_state;
            if(cnt==3'd7) cnt <= 3'b000;
            else if(state==DATA) cnt <= cnt + 3'b1;
            STOP2IDLE <= STOPPED;
        end
    end
    assign done = STOP2IDLE;
endmodule

```





### fsm serial datapath

题解：

```verilog
module top_module(
    input clk,
    input in,
    input reset,    // Synchronous reset
    output [7:0] out_byte,
    output done
); //

    // Use FSM from Fsm_serial
    parameter IDLE=4'b0001, DATA=4'b0010, STOP=4'b0100, ERR=4'b1000;
    reg [3:0] state;
    reg [3:0] next_state;
    reg [2:0] cnt;
    reg STOP2IDLE;
    reg [7:0] out_byte_buffer;
    wire STOPPED;
    assign STOPPED = in & (state == STOP);
    // transitional logic
    always@(*) begin
        case (state)
            IDLE:next_state = in ? IDLE : DATA;
            DATA:next_state = (cnt == 3'd7) ? STOP : DATA;
            STOP:next_state = in ? IDLE : ERR;
            ERR:next_state = in ? IDLE : ERR;		// until it finds stop bit (1)     
            default: next_state = state;
        endcase
    end
    always@(posedge clk) begin
        if(reset) begin
           state <= IDLE;
           cnt <= 3'b0;
            STOP2IDLE <= 1'b0;
        end
        else begin
           state <= next_state;
            if(cnt==3'd7) cnt <= 3'b000;
            else if(state==DATA) cnt <= cnt + 3'b1;
            STOP2IDLE <= STOPPED;
        end
    end
    assign done = STOP2IDLE;
    // New: Datapath to latch input bits.
    always@(posedge clk) begin
        if(reset) out_byte_buffer <= 8'b0;
        else if(state == DATA) out_byte_buffer <= {in, out_byte_buffer[7:1]};
    end
    assign out_byte = out_byte_buffer;
endmodule

```





##### FSM datapath with parity

```verilog
module top_module(
    input clk,
    input in,
    input reset,    // Synchronous reset
    output [7:0] out_byte,
    output done
); //

    // Modify FSM and datapath from Fsm_serialdata

    // Use FSM from Fsm_serial
    parameter IDLE=5'b00001, DATA=5'b00010, PARITY= 5'b00100, STOP=4'b01000, ERR=4'b10000;
    reg [3:0] state;
    reg [3:0] next_state;
    reg [2:0] cnt;
    reg STOP2IDLE;
    reg [7:0] out_byte_buffer;
    wire STOPPED;
    assign STOPPED = in & (state == STOP);
    // transitional logic
    always@(*) begin
        case (state)
            IDLE:next_state = in ? IDLE : DATA;
            DATA:next_state = (cnt == 3'd7) ? PARITY : DATA;
            PARITY:next_state = PARITY_TRUE ? STOP : IDLE;		// parity not correct, then return to IDLE
            STOP:next_state = in ? IDLE : ERR;
            ERR:next_state = in ? IDLE : ERR;		// until it finds stop bit (1)     
            default: next_state = state;
        endcase
    end
    always@(posedge clk) begin
        if(reset) begin
           state <= IDLE;
           cnt <= 3'b0;
            STOP2IDLE <= 1'b0;
        end
        else begin
           state <= next_state;
            if(cnt==3'd7) cnt <= 3'b000;
            else if(state==DATA) cnt <= cnt + 3'b1;
            else cnt <= 0;
            STOP2IDLE <= STOPPED;
        end
    end
    assign done = STOP2IDLE;
    // New: Datapath to latch input bits.
    always@(posedge clk) begin
        if(reset) out_byte_buffer <= 8'b0;
        else if(state == DATA) out_byte_buffer <= {in, out_byte_buffer[7:1]};
    end
    assign out_byte = out_byte_buffer;
    // New: Add parity checking.
    assign PARITY_TRUE = (~((^(out_byte_buffer)) ^ in)) & (STATE == PARITY);
    end
endmodule

```


