.org $E000
reset:
    SEI
    CLD
    LDX #$FF
    TXS
    LDA #$00
    STA $2000
    LDA #$00
    STA $2001
    LDA #$00
    STA $4010
warm0:
    LDA $2002
    AND #$80
    BEQ warm0
warm1:
    LDA $2002
    AND #$80
    BEQ warm1
    LDA #$00
    STA $0000
    LDA #$00
    STA $0001
    LDA #$00
    STA $0002
    LDA #$00
    STA $0003
    LDA #$00
    STA $0004
    LDA #$00
    STA $0005
    LDA $5784
    CMP #$E1
    BEQ supported
    LDA #$3F
    STA $2006
    LDA #$00
    STA $2006
    LDA #$16
    STA $2007
unsupported:
    JMP unsupported
supported:
    LDA #$20
    STA $2006
    LDA #$00
    STA $2006
    LDX #$00
map0:
    LDA $8000,X
    STA $2007
    INX
    BNE map0
    LDX #$00
map1:
    LDA $8100,X
    STA $2007
    INX
    BNE map1
    LDX #$00
map2:
    LDA $8200,X
    STA $2007
    INX
    BNE map2
    LDX #$00
map3:
    LDA $8300,X
    STA $2007
    INX
    BNE map3
    LDX #$00
map4:
    LDA $8400,X
    STA $2007
    INX
    BNE map4
    LDX #$00
map5:
    LDA $8500,X
    STA $2007
    INX
    BNE map5
    LDX #$00
map6:
    LDA $8600,X
    STA $2007
    INX
    BNE map6
    LDX #$00
map7:
    LDA $8700,X
    STA $2007
    INX
    BNE map7
    LDX #$00
map8:
    LDA $8800,X
    STA $2007
    INX
    BNE map8
    LDX #$00
map9:
    LDA $8900,X
    STA $2007
    INX
    BNE map9
    LDX #$00
map10:
    LDA $8A00,X
    STA $2007
    INX
    BNE map10
    LDX #$00
map11:
    LDA $8B00,X
    STA $2007
    INX
    BNE map11
    LDX #$00
map12:
    LDA $8C00,X
    STA $2007
    INX
    BNE map12
    LDX #$00
map13:
    LDA $8D00,X
    STA $2007
    INX
    BNE map13
    LDX #$00
map14:
    LDA $8E00,X
    STA $2007
    INX
    BNE map14
    LDX #$00
map15:
    LDA $8F00,X
    STA $2007
    INX
    BNE map15
    LDA #$00
    STA $5781
    LDA #$00
    STA $5782
    LDX #$00
desc0:
    LDA $A000,X
    STA $5783
    INX
    BNE desc0
    LDX #$00
desc1:
    LDA $A100,X
    STA $5783
    INX
    BNE desc1
    LDX #$00
desc2:
    LDA $A200,X
    STA $5783
    INX
    BNE desc2
    LDX #$00
desc3:
    LDA $A300,X
    STA $5783
    INX
    BNE desc3
    LDX #$00
desc4:
    LDA $A400,X
    STA $5783
    INX
    BNE desc4
    LDX #$00
desc5:
    LDA $A500,X
    STA $5783
    INX
    BNE desc5
    LDX #$00
desc6:
    LDA $A600,X
    STA $5783
    INX
    BNE desc6
    LDX #$00
desc7:
    LDA $A700,X
    STA $5783
    INX
    BNE desc7
    LDX #$00
desc8:
    LDA $A800,X
    STA $5783
    INX
    BNE desc8
    LDX #$00
desc9:
    LDA $A900,X
    STA $5783
    INX
    BNE desc9
    LDX #$00
desc10:
    LDA $AA00,X
    STA $5783
    INX
    BNE desc10
    LDX #$00
desc11:
    LDA $AB00,X
    STA $5783
    INX
    BNE desc11
    LDX #$00
desc12:
    LDA $AC00,X
    STA $5783
    INX
    BNE desc12
    LDX #$00
desc13:
    LDA $AD00,X
    STA $5783
    INX
    BNE desc13
    LDX #$00
desc14:
    LDA $AE00,X
    STA $5783
    INX
    BNE desc14
    LDX #$00
desc15:
    LDA $AF00,X
    STA $5783
    INX
    BNE desc15
    LDA #$03
    STA $5780
    LDA #$3F
    STA $2006
    LDA #$00
    STA $2006
    LDA #$0F
    STA $2007
    LDA #$07
    STA $2007
    LDA #$17
    STA $2007
    LDA #$37
    STA $2007
    LDA #$0F
    STA $2007
    LDA #$01
    STA $2007
    LDA #$11
    STA $2007
    LDA #$31
    STA $2007
    LDA #$0F
    STA $2007
    LDA #$06
    STA $2007
    LDA #$16
    STA $2007
    LDA #$26
    STA $2007
    LDA #$0F
    STA $2007
    LDA #$0B
    STA $2007
    LDA #$1A
    STA $2007
    LDA #$29
    STA $2007
    LDA $2002
    LDA #$00
    STA $2005
    LDA #$00
    STA $2005
    LDA #$80
    STA $2000
    LDA #$0A
    STA $2001
loop:
    JMP loop
nmi:
    PHA
    TXA
    PHA
    TYA
    PHA
    INC $00
    LDA $05
    AND #$01
    BNE vertical
    INC $01
    BNE scroll
    LDA $02
    EOR #$01
    STA $02
    BNE scroll
    INC $05
    JMP scroll
vertical:
    INC $03
    LDA $03
    CMP #$F0
    BNE scroll
    LDA #$00
    STA $0003
    LDA $04
    EOR #$02
    STA $04
    BNE scroll
    INC $05
scroll:
    LDA $2002
    LDA $01
    STA $2005
    LDA $03
    STA $2005
    LDA $02
    ORA #$80
    STA $06
    LDA $04
    ORA $06
    STA $2000
    PLA
    TAY
    PLA
    TAX
    PLA
    RTI
irq:
    RTI