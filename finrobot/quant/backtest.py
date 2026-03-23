from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import pandas as pd
from .portfolio import optimize_portfolio

@dataclass
class FoldResult:
    fold_id:      int
    train_start:  pd.Timestamp
    train_end:    pd.Timestamp
    test_start:   pd.Timestamp
    test_end:     pd.Timestamp
    sharpe:       float
    max_drawdown: float
    hit_rate:     float
    weights:      np.ndarray

@dataclass
class WFTResult:
    folds:       List[FoldResult]
    mean_sharpe: float
    ci_sharpe:   Tuple[float, float]   # 95% CI
    mean_dd:     float

class WalkForwardBacktest:
    def __init__(self, train_window=252, test_window=63, step=63):
        self.train_window = train_window
        self.test_window  = test_window
        self.step         = step

    def run(self, returns_df: pd.DataFrame) -> WFTResult:
        """
        Executes a Walk-Forward Test (WFT) on the provided returns data.
        returns_df: DataFrame where columns are asset tickers and rows are dates.
        """
        folds = []
        start = 0
        n_obs = len(returns_df)
        
        while start + self.train_window + self.test_window <= n_obs:
            # Training window (optimization)
            train = returns_df.iloc[start : start + self.train_window]
            # Testing window (evaluation)
            test  = returns_df.iloc[start + self.train_window : 
                                 start + self.train_window + self.test_window]
            
            # 1. Optimize portfolio on training data (Mean-Variance with Shrinkage)
            weights = optimize_portfolio(train.values, method='sharpe', use_shrinkage=True)
            
            # 2. Evaluate on test data (Out-of-sample)
            # test.values is (T_test, N_assets), weights is (N_assets,)
            # portfolio_returns is (T_test,)
            portfolio_returns = test.values @ weights
            
            fold_id = len(folds)
            fold_res = self._compute_fold(
                fold_id, train, test, weights, portfolio_returns
            )
            folds.append(fold_res)
            
            # Advance start by the specified step (sliding window)
            start += self.step
            
        if not folds:
            raise ValueError("Insufficient data for at least one fold of WFT.")
            
        return self._aggregate(folds)

    def _compute_fold(self, fold_id: int, train: pd.DataFrame, test: pd.DataFrame, 
                      weights: np.ndarray, p_returns_arr: np.ndarray) -> FoldResult:
        # Convert to Series for convenience and index alignment
        p_returns = pd.Series(p_returns_arr, index=test.index)
        
        # Annualized Sharpe: (mean / std) * sqrt(252)
        std = p_returns.std()
        sharpe = (p_returns.mean() / std * np.sqrt(252)) if std > 1e-10 else 0.0
        
        # Max Drawdown
        cum_ret = (1 + p_returns).cumprod()
        running_max = cum_ret.cummax()
        drawdown = (cum_ret - running_max) / running_max
        max_dd = drawdown.min()
        
        # Hit Rate: percentage of positive returns
        hit_rate = (p_returns > 0).mean()
        
        return FoldResult(
            fold_id=fold_id,
            train_start=train.index[0],
            train_end=train.index[-1],
            test_start=test.index[0],
            test_end=test.index[-1],
            sharpe=sharpe,
            max_drawdown=max_dd,
            hit_rate=hit_rate,
            weights=weights
        )

    def _aggregate(self, folds: List[FoldResult]) -> WFTResult:
        sharpes = [f.sharpe for f in folds]
        mean_sharpe = np.mean(sharpes)
        std_sharpe = np.std(sharpes)
        
        # 95% Confidence Interval for mean Sharpe (assuming normal distribution across folds)
        # Margin of error = 1.96 * (std / sqrt(n))
        me = 1.96 * (std_sharpe / np.sqrt(len(folds))) if len(folds) > 1 else 0.0
        ci = (mean_sharpe - me, mean_sharpe + me)
        
        mean_dd = np.mean([f.max_drawdown for f in folds])
        
        return WFTResult(
            folds=folds,
            mean_sharpe=mean_sharpe,
            ci_sharpe=ci,
            mean_dd=mean_dd
        )
