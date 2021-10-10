const SPACE: char = ' ';
const PLUS: char = '+';
const MINUS: char = '-';
const MULT: char = '*';
const DIV: char = '/';

const TOKEN_EOF: Token = Token{ttype: TokenType::EOF, value: TokenValue::Eof};
const TOKEN_PLUS: Token = Token{ttype: TokenType::OPERATOR, value: TokenValue::Plus};
const TOKEN_MINUS: Token = Token{ttype: TokenType::OPERATOR, value: TokenValue::Minus};
const TOKEN_MULT: Token = Token{ttype: TokenType::OPERATOR, value: TokenValue::Mult};
const TOKEN_DIV: Token = Token{ttype: TokenType::OPERATOR, value: TokenValue::Div};

enum TokenType {
    INTEGER,
    OPERATOR,
    EOF,
}

#[derive(Debug)]
enum TokenValue {
    Integer(i64),
    Plus,
    Minus,
    Mult,
    Div,
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

fn validate_token_type(token: &Token, ttype: TokenType) {
    match (&token.ttype, ttype) {
        (TokenType::INTEGER, TokenType::INTEGER) => {},
        (TokenType::OPERATOR, TokenType::OPERATOR) => {},
        (TokenType::EOF, TokenType::EOF) => {},
        _ => panic!("Unexpected token type.")
    }

}

fn chars_to_integer(source: &mut Source) -> i64 {
    let mut integer_text = String::new();
    loop {
        let current_char = source.text.chars().nth(source.index).expect("No more chars.");
        match current_char {
            '0'..='9' => {
                source.inc_index();
                integer_text.push_str((format!("{}", current_char)).as_str());

                if source.index == source.text.len() {
                    break
                }

            },
            _ => break,
        }
    }
    integer_text.to_string().parse::<i64>().unwrap()
}

fn get_next_token(source: &mut Source) -> Token {
    if source.index >= source.text.len() {
        return TOKEN_EOF
    }
    let mut current_char: char;
    loop {
        current_char = source.text.chars().nth(source.index).expect("No more chars.");
        match current_char {
            SPACE => { source.inc_index() },
            _ => { break },
        }
    }

    let token = match current_char {
        '0'..='9' => {
            Token::new(TokenType::INTEGER, TokenValue::Integer(chars_to_integer(source)))
        },
        PLUS => { source.inc_index(); TOKEN_PLUS }
        MINUS => { source.inc_index(); TOKEN_MINUS }
        MULT => { source.inc_index(); TOKEN_MULT }
        DIV => { source.inc_index(); TOKEN_DIV }
        _ => panic!("--> bad char, index: {}.", source.index),
    };
    token
}

fn factor(source: &mut Source) -> i64 {
    let left_token = get_next_token(source);
    validate_token_type(&left_token, TokenType::INTEGER);
    let result = match left_token.value {
        TokenValue::Integer(x) => x,
        _ => { panic!("Bad token value.")},
    };
    result
}

fn term(source: &mut Source) -> i64 {
    let mut result = factor(source);
    loop {
        let index = source.index;
        let token = get_next_token(source);
        match token.value {
            TokenValue::Mult => { result *= factor(source) },
            TokenValue::Div => { result /= factor(source) },
            _ => {source.index = index; break },
        };
    }

    result
}

fn expr(source: &mut Source) -> i64 {
    let mut result = term(source);
    loop {
        let index = source.index;
        let token = get_next_token(source);
        match token.value {
            TokenValue::Plus => { result += term(source) },
            TokenValue::Minus => { result -= term(source) },
            _ => {source.index = index; break },
        };
    }

    result
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
    match token.ttype { TokenType::OPERATOR => assert!(true), _ => assert!(false), };
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

#[test]
fn test_multi_operator_expression() {
    assert_eq!(expr(&mut Source::new(String::from("123  +      456 - 1 + 11    - 2   +  34"))), 123+456-1+11-2+34);
}

#[test]
fn test_mult_div() {
    assert_eq!(expr(&mut Source::new(String::from("4/2"))), 4/2);
    assert_eq!(expr(&mut Source::new(String::from("400 / 3"))), 400/3);
}

#[test]
fn test_plus_minus_mult_div_operator_precedence() {
    assert_eq!(expr(&mut Source::new(String::from("1+1*10"))), 1+1*10);
    assert_eq!(expr(&mut Source::new(String::from("1+0*10-5"))), 1+0*10-5);
}
