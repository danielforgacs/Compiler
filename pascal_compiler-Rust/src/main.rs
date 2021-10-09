enum TokenType {
    INTEGER,
    PLUS,
    MINUS,
    EOF,
}

#[derive(Debug)]
enum TokenValue {
    Integer(i64),
    Plus,
    Minus,
    Eof,
}

struct Token {
    ttype: TokenType,
    value: TokenValue,
}

struct Source {
    text: String,
    index: usize,
}

impl Source {
    fn new(text: String) -> Self {
        Source {
            text,
            index: 0,
        }
    }
}

impl Token {
    fn new(ttype: TokenType, value: TokenValue) -> Self {
        Token {
            ttype: ttype,
            value: value,
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mut source = Source::new(String::from("1+2"));
    if args.len() == 2 {
        source.text = args[1].to_string();
    }
    let result = expr(source);
    println!("result: {}", result);
}

fn expr(source: Source) -> i64 {
    let (left_token, source) = get_next_token(source);
    let left_value = match left_token.value {
        TokenValue::Integer(x) => x,
        _ => { panic!("Bad left expr token value") }
    };

    let (op, source) = get_next_token(source);
    let op = match op.value {
        TokenValue::Plus => '+',
        TokenValue::Minus => '-',
        _ => { panic!("Bad op expr token value") }
    };

    let (right_token, source) = get_next_token(source);
    let right_value = match right_token.value {
        TokenValue::Integer(x) => x,
        _ => { panic!("Bad right expr token value") }
    };

    let mut result: i64;
    if op == '+' {
        result = left_value + right_value;
    } else {
        result = left_value - right_value;
    }
    result
}

fn get_next_token(mut source: Source) -> (Token, Source) {
    if source.index >= source.text.len() {
        return (
            Token {
                ttype: TokenType::EOF,
                value: TokenValue::Eof,
            },
            source
        )
    }
    let current_char = source
        .text
        .chars()
        .nth(source.index)
        .expect("No more chars.");
    match current_char {
        '0'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9' => {
            source.index += 1;
            return (Token {
                ttype: TokenType::INTEGER,
                value: TokenValue::Integer(
                    current_char.to_string().parse::<i64>().unwrap()
                ),
            }, source)
        },
        '+' => {
            source.index += 1;
            return (Token {
                ttype: TokenType::PLUS,
                value: TokenValue::Plus,
            }, source)
        }
        '-' => {
            source.index += 1;
            return (Token {
                ttype: TokenType::MINUS,
                value: TokenValue::Minus,
            }, source)
        }
        _ => panic!("Illegal character."),
    };
}

#[test]
fn test_token() {
    let tok = Token::new(TokenType::EOF, TokenValue::Eof);
}

#[test]
fn test_next_token_empty_source() {
    let (token, source) = get_next_token(Source::new(String::from("")));
    assert_eq!(source.index, 0);
    match token.ttype { TokenType::EOF => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Eof => assert!(true), _ => assert!(false), };
}

#[test]
fn test_next_token_gets_digit() {
    let (token, source) = get_next_token(Source::new(String::from("0")));
    assert_eq!(source.index, 1);
    match token.ttype { TokenType::INTEGER => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Integer(0) => assert!(true), _ => assert!(false), };

    let (token, source) = get_next_token(Source::new(String::from("1")));
    assert_eq!(source.index, 1);
    match token.ttype { TokenType::INTEGER => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Integer(1) => assert!(true), _ => assert!(false), };

    let (token, source) = get_next_token(Source::new(String::from("+")));
    assert_eq!(source.index, 1);
    match token.ttype { TokenType::PLUS => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Plus => assert!(true), _ => assert!(false), };
}

#[test]
fn text_expression() {
    assert_eq!(expr(Source::new(String::from("1+2"))), 1+2);
    assert_eq!(expr(Source::new(String::from("3+2"))), 3+2);
    assert_eq!(expr(Source::new(String::from("9+7"))), 9+7);
}
