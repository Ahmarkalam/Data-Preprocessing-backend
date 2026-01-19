import re
import nltk
from pathlib import Path
from typing import List, Optional, Dict
from collections import Counter
from src.utils.logger import get_logger
from src.core.models import QualityMetrics, ProcessingConfig

logger = get_logger("text_processor")

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    logger.warning("Could not download NLTK data")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class TextProcessor:
    """Handles text preprocessing operations"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def load_text(self, file_path: str) -> str:
        """Load text from file"""
        try:
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                text = f.read()
            logger.info(f"Loaded text from {file_path}, length: {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"Error loading text from {file_path}: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'-]', '', text)
        
        logger.debug("Cleaned text")
        return text
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        text = re.sub(url_pattern, '', text)
        return text
    
    def remove_emails(self, text: str) -> str:
        """Remove email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text = re.sub(email_pattern, '', text)
        return text
    
    def to_lowercase(self, text: str) -> str:
        """Convert text to lowercase"""
        return text.lower()
    
    def remove_numbers(self, text: str) -> str:
        """Remove numbers from text"""
        return re.sub(r'\d+', '', text)
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        tokens = word_tokenize(text)
        logger.debug(f"Tokenized into {len(tokens)} tokens")
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove common stopwords"""
        filtered = [word for word in tokens if word.lower() not in self.stop_words]
        logger.debug(f"Removed stopwords: {len(tokens)} -> {len(filtered)} tokens")
        return filtered
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens to base form"""
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        return lemmatized
    
    def get_word_frequency(self, tokens: List[str], top_n: int = 50) -> Dict[str, int]:
        """Get word frequency distribution"""
        freq = Counter(tokens)
        return dict(freq.most_common(top_n))
    
    def process(self, input_path: str, output_path: str,
                lowercase: bool = True,
                remove_stopwords: bool = True,
                lemmatize: bool = False) -> QualityMetrics:
        """Main text processing pipeline"""
        logger.info(f"Starting text processing: {input_path}")
        
        # Load text
        text = self.load_text(input_path)
        original_length = len(text)
        
        # Clean text
        text = self.clean_text(text)
        text = self.remove_urls(text)
        text = self.remove_emails(text)
        
        # Lowercase
        if lowercase:
            text = self.to_lowercase(text)
        
        # Tokenize
        tokens = self.tokenize(text)
        original_token_count = len(tokens)
        
        # Remove stopwords
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        if lemmatize:
            tokens = self.lemmatize(tokens)
        
        # Reconstruct text
        processed_text = ' '.join(tokens)
        
        # Save processed text
        with open(output_path, 'w', encoding=self.config.encoding) as f:
            f.write(processed_text)
        
        logger.info(f"Saved processed text to: {output_path}")
        
        # Calculate metrics
        final_length = len(processed_text)
        reduction_percent = ((original_length - final_length) / original_length * 100) if original_length > 0 else 0
        
        issues = []
        if reduction_percent > 50:
            issues.append(f"High text reduction: {reduction_percent:.2f}%")
        
        quality_score = 1.0 if final_length > 0 else 0.0
        
        metrics = QualityMetrics(
            total_records=original_token_count,
            valid_records=len(tokens),
            invalid_records=original_token_count - len(tokens),
            missing_values_percent=0.0,
            duplicate_percent=0.0,
            quality_score=quality_score,
            issues=issues
        )
        
        logger.info(f"Text processing complete. Quality score: {quality_score}")
        return metrics