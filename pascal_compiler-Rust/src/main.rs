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

    if args.len() != 2 {
        println!("No Source... Bye!");
    } else {
        let source = Source::new(String::from(args[1].to_string()));
        let result = expr(source);
        println!("result: {}", result);
    }
}

fn expr(source: Source) -> i64 {
    let (left_token, source) = get_next_token(source);
    let left_value = match left_token.value {
        TokenValue::Integer(x) => x,
        _ => {
            panic!(
                "\n\n[ERROR] BAD EXPRESSION LEFT VALUE. SOURCE: '{}', INDEX: {}. TOKE VALUE: '{:?}'.\n\n",
                 source.text, source.index, left_token.value)
            }
    };

    let (op, source) = get_next_token(source);
    let op = match op.value {
        TokenValue::Plus => '+',
        TokenValue::Minus => '-',
        _ => { panic!("\n\n[ERROR] MISSING '-' OR '+' FROM EXPR. SOURCE: '{}', INDEX: {}.\n\n", source.text, source.index) }
    };

    let (right_token, source) = get_next_token(source);
    let right_value = match right_token.value {
        TokenValue::Integer(x) => x,
        _ => {
            panic!(
                "\n\n[ERROR] BAD EXPRESSION RIGHT VALUE. SOURCE: '{}', INDEX: {}. TOKE VALUE: '{:?}'.\n\n",
                 source.text, source.index, right_token.value)
            }
    };

    let result: i64;
    if op == '+' {
        result = left_value + right_value;
    } else {
        result = left_value - right_value;
    }
    result
}

fn integer(mut source: &mut Source) -> (usize, TokenValue) {
    let mut integer_text = String::new();
    loop {
        let current_char = source
            .text
            .chars()
            .nth(source.index)
            .expect("No more chars.");
        match current_char {
            '0'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9' => {
                source.index += 1;
                integer_text.push_str((format!("{}", current_char)).as_str());
                if source.index == source.text.len() {
                    break
                }

            },
            _ => {break},
        }
    }
    let value = integer_text.to_string().parse::<i64>().unwrap();
    (source.index, TokenValue::Integer(value))
}

fn get_next_token(mut source: Source) -> (Token, Source) {
    if source.index >= source.text.len() {
        return (Token::new(TokenType::EOF, TokenValue::Eof), source)
    }

    let mut current_char: char;
    loop {
        current_char = source
            .text
            .chars()
            .nth(source.index)
            .expect("No more chars.");
        match current_char {
            ' ' => {source.index += 1},
            _ => {break},
        }
    }

    match current_char {
        '0'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9' => {
            let (index, value) = integer(&mut source);
            source.index = index;
            return (Token::new(TokenType::INTEGER, value), source)
        },
        '+' => {
            source.index += 1;
            return (Token::new(TokenType::PLUS, TokenValue::Plus), source)
        }
        '-' => {
            source.index += 1;
            return (Token::new(TokenType::MINUS, TokenValue::Minus), source)
        }
        _ => panic!(
                "\n\n[ERROR] ILLEGAL CHARACTER: '{}', SOURCE: '{}' INDEX: {}.\n\n",
                current_char, source.text, source.index
            ),
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
fn test_expression() {
    assert_eq!(expr(Source::new(String::from("1+2"))), 1+2);
    assert_eq!(expr(Source::new(String::from("3+2"))), 3+2);
    assert_eq!(expr(Source::new(String::from("9+7"))), 9+7);
    assert_eq!(expr(Source::new(String::from("9-7"))), 9-7);
}

#[test]
fn test_skip_whitespace() {
    assert_eq!(expr(Source::new(String::from("9 -7"))), 9-7);
    assert_eq!(expr(Source::new(String::from("9   -            7"))), 9-7);
}

#[test]
fn test_multi_digit_integer_token() {
    let (token, source) = get_next_token(Source::new(String::from("1234")));
    assert_eq!(source.index, 4);
    match token.ttype { TokenType::INTEGER => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Integer(1234) => assert!(true), _ => assert!(false), };
}

#[test]
fn test_multi_digit_integers_plus_minus() {
    assert_eq!(expr(Source::new(String::from("123+456"))), 123+456);
    assert_eq!(expr(Source::new(String::from("123  +       456"))), 123+456);
}
