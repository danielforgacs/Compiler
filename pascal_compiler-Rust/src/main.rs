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

    fn inc_index(&mut self) {
        self.index += 1;
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
        let mut source = Source::new(String::from(args[1].to_string()));
        let result = expr(&mut source);
        println!("result: {}", result);
    }
}

fn expr(source: &mut Source) -> i64 {
    let left_token = get_next_token(source);
    let left_value = match left_token.value {
        TokenValue::Integer(x) => x,
        _ => { panic!("--> expr bad left value, index: {}.", source.index) }
    };
    let operator = get_next_token(source);
    let right_token = get_next_token(source);
    let right_value = match right_token.value {
        TokenValue::Integer(x) => x,
        _ => { panic!("--> expr bad right value, index: {}.", source.index) }
    };

    let result = match operator.value {
        TokenValue::Plus => { left_value + right_value },
        TokenValue::Minus => { left_value - right_value },
        _ => { panic!("--> expr bad operator, index: {}.", source.index) }
    };
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

fn get_next_token(source: &mut Source) -> Token {
    if source.index >= source.text.len() {
        return Token::new(TokenType::EOF, TokenValue::Eof)
    }
    let mut current_char: char;
    loop {
        current_char = source.text.chars().nth(source.index).expect("No more chars.");
        match current_char {
            ' ' => { source.inc_index() },
            _ => { break },
        }
    }

    match current_char {
        '0'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9' => {
            let (index, value) = integer(source);
            source.index = index;
            return Token::new(TokenType::INTEGER, value)
        },
        '+' => {
            source.inc_index();
            return Token::new(TokenType::PLUS, TokenValue::Plus)
        }
        '-' => {
            source.inc_index();
            return Token::new(TokenType::MINUS, TokenValue::Minus)
        }
        _ => panic!("--> bad char, index: {}.", source.index),
    };
}

#[test]
fn test_token() {
    Token::new(TokenType::EOF, TokenValue::Eof);
}

#[test]
fn test_next_token_empty_source() {
    let mut source = Source::new(String::from(""));
    let token = get_next_token(&mut source);
    assert_eq!(source.index, 0);
    match token.ttype { TokenType::EOF => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Eof => assert!(true), _ => assert!(false), };
}

#[test]
fn test_next_token_gets_digit() {
    let mut source = Source::new(String::from("0"));
    let token = get_next_token(&mut source);
    assert_eq!(source.index, 1);
    match token.ttype { TokenType::INTEGER => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Integer(0) => assert!(true), _ => assert!(false), };

    let mut source = Source::new(String::from("1"));
    let token = get_next_token(&mut source);
    assert_eq!(source.index, 1);
    match token.ttype { TokenType::INTEGER => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Integer(1) => assert!(true), _ => assert!(false), };

    let mut source = Source::new(String::from("+"));
    let token = get_next_token(&mut source);
    assert_eq!(source.index, 1);
    match token.ttype { TokenType::PLUS => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Plus => assert!(true), _ => assert!(false), };
}

#[test]
fn test_expression() {
    assert_eq!(expr(&mut Source::new(String::from("1+2"))), 1+2);
    assert_eq!(expr(&mut Source::new(String::from("3+2"))), 3+2);
    assert_eq!(expr(&mut Source::new(String::from("9+7"))), 9+7);
    assert_eq!(expr(&mut Source::new(String::from("9-7"))), 9-7);
}

#[test]
fn test_skip_whitespace() {
    assert_eq!(expr(&mut Source::new(String::from("9 -7"))), 9-7);
    assert_eq!(expr(&mut Source::new(String::from("9   -            7"))), 9-7);
}

#[test]
fn test_multi_digit_integer_token() {
    let mut source = Source::new(String::from("1234"));
    let token = get_next_token(&mut source);
    assert_eq!(source.index, 4);
    match token.ttype { TokenType::INTEGER => assert!(true), _ => assert!(false), };
    match token.value { TokenValue::Integer(1234) => assert!(true), _ => assert!(false), };
}

#[test]
fn test_multi_digit_integers_plus_minus() {
    assert_eq!(expr(&mut Source::new(String::from("123+456"))), 123+456);
    assert_eq!(expr(&mut Source::new(String::from("123  +       456"))), 123+456);
}

#[test]
fn test_token_mutability_and_index() {
    let mut source = Source::new(String::from(""));
    assert_eq!(source.index, 0);
    source.inc_index();
    assert_eq!(source.index, 1);
    source.inc_index();
    assert_eq!(source.index, 2);
    source.inc_index();
    assert_eq!(source.index, 3);

    source.index = 10;
    assert_eq!(source.index, 10);
    source.index = 20;
    assert_eq!(source.index, 20);
    source.index = 30;
    assert_eq!(source.index, 30);
    source.index = 40;
    assert_eq!(source.index, 40);
}
