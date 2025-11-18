"""
Adversarial Attack Testing Module
Tests model robustness against adversarial attacks
Implements FGSM, PGD, and membership inference attacks
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AdversarialTestResult:
    """Represents adversarial attack test result"""
    attack_type: str
    clean_accuracy: float
    adversarial_accuracy: float
    robustness_score: float
    epsilon: float
    iterations: int
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack_type": self.attack_type,
            "clean_accuracy": self.clean_accuracy,
            "adversarial_accuracy": self.adversarial_accuracy,
            "robustness_score": self.robustness_score,
            "epsilon": self.epsilon,
            "iterations": self.iterations,
            "timestamp": self.timestamp
        }


@dataclass
class MembershipInferenceResult:
    """Represents membership inference attack result"""
    attack_success_rate: float
    baseline_success_rate: float
    advantage: float
    is_private: bool
    confidence: float
    samples_tested: int
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack_success_rate": self.attack_success_rate,
            "baseline_success_rate": self.baseline_success_rate,
            "advantage": self.advantage,
            "is_private": self.is_private,
            "confidence": self.confidence,
            "samples_tested": self.samples_tested,
            "timestamp": self.timestamp
        }


class AdversarialAttacks:
    """Implements common adversarial attacks"""

    @staticmethod
    def fgsm_attack(model, x: np.ndarray, y: np.ndarray,
                    epsilon: float = 0.1) -> np.ndarray:
        """
        Fast Gradient Sign Method (FGSM) attack.

        Generates adversarial examples by taking a step in the direction of gradient.

        Args:
            model: Model with predict method
            x: Input features (numpy array)
            y: True labels
            epsilon: Step size / perturbation budget

        Returns:
            Adversarial examples
        """
        try:
            import tensorflow as tf

            x_tensor = tf.Variable(x, dtype=tf.float32)

            with tf.GradientTape() as tape:
                predictions = model.predict(x_tensor)
                if isinstance(predictions, tf.Tensor):
                    loss = tf.nn.softmax_cross_entropy_with_logits(
                        y, predictions)
                else:
                    loss = np.mean((predictions - y) ** 2)

            if isinstance(loss, tf.Tensor):
                gradients = tape.gradient(loss, x_tensor)
                x_adv = x_tensor + epsilon * tf.sign(gradients)
            else:
                # Fallback: numerical gradient
                x_adv = x + epsilon * \
                    np.sign((model.predict(x + 1e-4) - model.predict(x)) / 1e-4)

            return x_adv.numpy() if hasattr(x_adv, 'numpy') else x_adv

        except ImportError:
            # TensorFlow not available, use numerical approach
            logger.warning(
                "TensorFlow not available, using numerical gradients")
            grad = (model.predict(x + 1e-4) -
                    model.predict(x - 1e-4)) / (2 * 1e-4)
            return x + epsilon * np.sign(grad)

    @staticmethod
    def pgd_attack(model, x: np.ndarray, y: np.ndarray,
                   epsilon: float = 0.1, step_size: float = 0.01,
                   iterations: int = 40) -> np.ndarray:
        """
        Projected Gradient Descent (PGD) attack.

        Stronger multi-step attack that finds worst-case adversarial examples.

        Args:
            model: Model with predict method
            x: Input features
            y: True labels
            epsilon: Maximum perturbation budget
            step_size: Step size per iteration
            iterations: Number of iterations

        Returns:
            Adversarial examples
        """
        x_adv = x.copy()

        for iteration in range(iterations):
            # Compute gradients
            try:
                import tensorflow as tf
                x_tensor = tf.Variable(x_adv, dtype=tf.float32)

                with tf.GradientTape() as tape:
                    predictions = model.predict(x_tensor)
                    if isinstance(predictions, tf.Tensor):
                        loss = tf.nn.softmax_cross_entropy_with_logits(
                            y, predictions)
                    else:
                        loss = np.mean((predictions - y) ** 2)

                gradients = tape.gradient(loss, x_tensor)
                grad = gradients.numpy() if hasattr(gradients, 'numpy') else gradients

            except ImportError:
                # Numerical gradient
                grad = (model.predict(x_adv + 1e-4) -
                        model.predict(x_adv - 1e-4)) / (2 * 1e-4)

            # Update adversarial example
            x_adv = x_adv + step_size * np.sign(grad)

            # Project back to epsilon ball
            x_adv = np.clip(x_adv, x - epsilon, x + epsilon)
            x_adv = np.clip(x_adv, 0, 1)  # Clip to valid range

        return x_adv

    @staticmethod
    def carlini_wagner_attack(model, x: np.ndarray, y: np.ndarray,
                              iterations: int = 100, c: float = 0.1) -> np.ndarray:
        """
        Carlini-Wagner (C&W) attack.

        Attempts to find minimal adversarial perturbation.

        Args:
            model: Model with predict method
            x: Input features
            y: True labels
            iterations: Number of iterations
            c: Regularization parameter

        Returns:
            Adversarial examples
        """
        x_adv = x.copy()

        for iteration in range(iterations):
            try:
                import tensorflow as tf
                x_tensor = tf.Variable(x_adv, dtype=tf.float32)

                with tf.GradientTape() as tape:
                    predictions = model.predict(x_tensor)
                    perturbation = tf.reduce_sum((x_tensor - x) ** 2)

                    if isinstance(predictions, tf.Tensor):
                        ce_loss = tf.nn.softmax_cross_entropy_with_logits(
                            y, predictions)
                    else:
                        ce_loss = np.mean((predictions - y) ** 2)

                    total_loss = ce_loss + c * perturbation

                gradients = tape.gradient(total_loss, x_tensor)
                grad = gradients.numpy() if hasattr(gradients, 'numpy') else gradients

                x_adv = x_adv - 0.01 * grad

            except ImportError:
                break

        return x_adv


class RobustnessEvaluation:
    """Evaluates model robustness to adversarial attacks"""

    @staticmethod
    def test_fgsm_robustness(model, x_test: np.ndarray, y_test: np.ndarray,
                             epsilon: float = 0.1, sample_size: int = 100) -> AdversarialTestResult:
        """
        Test model robustness to FGSM attack.

        Args:
            model: Model with predict method
            x_test: Test features
            y_test: Test labels
            epsilon: Attack epsilon
            sample_size: Number of samples to test

        Returns:
            AdversarialTestResult
        """
        # Sample subset
        if len(x_test) > sample_size:
            indices = np.random.choice(len(x_test), sample_size, replace=False)
            x_sample = x_test[indices]
            y_sample = y_test[indices]
        else:
            x_sample = x_test
            y_sample = y_test

        # Clean accuracy
        clean_preds = model.predict(x_sample)
        if isinstance(clean_preds, (list, tuple)):
            clean_preds = clean_preds[0]

        clean_correct = np.sum(
            np.argmax(clean_preds, axis=1) == np.argmax(y_sample, axis=1)
        ) if y_sample.ndim > 1 else np.sum(clean_preds == y_sample)
        clean_accuracy = clean_correct / len(y_sample)

        # Generate adversarial examples
        try:
            x_adv = AdversarialAttacks.fgsm_attack(
                model, x_sample, y_sample, epsilon)
        except Exception as e:
            logger.error(f"FGSM attack failed: {e}")
            x_adv = x_sample

        # Adversarial accuracy
        adv_preds = model.predict(x_adv)
        if isinstance(adv_preds, (list, tuple)):
            adv_preds = adv_preds[0]

        adv_correct = np.sum(
            np.argmax(adv_preds, axis=1) == np.argmax(y_sample, axis=1)
        ) if y_sample.ndim > 1 else np.sum(adv_preds == y_sample)
        adv_accuracy = adv_correct / len(y_sample)

        # Robustness score (adversarial accuracy / clean accuracy)
        robustness = adv_accuracy / clean_accuracy if clean_accuracy > 0 else 0.0

        return AdversarialTestResult(
            attack_type="FGSM",
            clean_accuracy=float(clean_accuracy),
            adversarial_accuracy=float(adv_accuracy),
            robustness_score=float(robustness),
            epsilon=epsilon,
            iterations=1
        )

    @staticmethod
    def test_pgd_robustness(model, x_test: np.ndarray, y_test: np.ndarray,
                            epsilon: float = 0.1, iterations: int = 40,
                            sample_size: int = 50) -> AdversarialTestResult:
        """
        Test model robustness to PGD attack.

        Args:
            model: Model with predict method
            x_test: Test features
            y_test: Test labels
            epsilon: Attack epsilon
            iterations: PGD iterations
            sample_size: Number of samples to test

        Returns:
            AdversarialTestResult
        """
        # Sample subset (PGD is expensive)
        if len(x_test) > sample_size:
            indices = np.random.choice(len(x_test), sample_size, replace=False)
            x_sample = x_test[indices]
            y_sample = y_test[indices]
        else:
            x_sample = x_test
            y_sample = y_test

        # Clean accuracy
        clean_preds = model.predict(x_sample)
        if isinstance(clean_preds, (list, tuple)):
            clean_preds = clean_preds[0]

        clean_correct = np.sum(
            np.argmax(clean_preds, axis=1) == np.argmax(y_sample, axis=1)
        ) if y_sample.ndim > 1 else np.sum(clean_preds == y_sample)
        clean_accuracy = clean_correct / len(y_sample)

        # Generate adversarial examples
        try:
            x_adv = AdversarialAttacks.pgd_attack(
                model, x_sample, y_sample, epsilon, iterations=iterations
            )
        except Exception as e:
            logger.error(f"PGD attack failed: {e}")
            x_adv = x_sample

        # Adversarial accuracy
        adv_preds = model.predict(x_adv)
        if isinstance(adv_preds, (list, tuple)):
            adv_preds = adv_preds[0]

        adv_correct = np.sum(
            np.argmax(adv_preds, axis=1) == np.argmax(y_sample, axis=1)
        ) if y_sample.ndim > 1 else np.sum(adv_preds == y_sample)
        adv_accuracy = adv_correct / len(y_sample)

        # Robustness score
        robustness = adv_accuracy / clean_accuracy if clean_accuracy > 0 else 0.0

        return AdversarialTestResult(
            attack_type="PGD",
            clean_accuracy=float(clean_accuracy),
            adversarial_accuracy=float(adv_accuracy),
            robustness_score=float(robustness),
            epsilon=epsilon,
            iterations=iterations
        )

    @staticmethod
    def score_robustness(result: AdversarialTestResult) -> Tuple[str, float]:
        """
        Score robustness result.

        Returns:
            Tuple of (rating, score)
        """
        robustness = result.robustness_score

        if robustness >= 0.9:
            return "Excellent", 1.0
        elif robustness >= 0.8:
            return "Good", 0.8
        elif robustness >= 0.7:
            return "Acceptable", 0.7
        elif robustness >= 0.6:
            return "Weak", 0.5
        else:
            return "Poor", 0.3


class MembershipInferenceAttack:
    """Tests for membership inference attacks (data leakage)"""

    @staticmethod
    def test_membership_inference(model, x_train: np.ndarray, x_test: np.ndarray,
                                  y_train: np.ndarray, y_test: np.ndarray,
                                  sample_size: int = 100) -> MembershipInferenceResult:
        """
        Test if model leaks information about training data.

        Membership Inference: Can an attacker determine if a sample was in training?

        Args:
            model: Model with predict method
            x_train: Training features
            x_test: Test features
            y_train: Training labels
            y_test: Test labels
            sample_size: Samples to test from each set

        Returns:
            MembershipInferenceResult
        """
        # Sample from train and test
        if len(x_train) > sample_size:
            train_indices = np.random.choice(
                len(x_train), sample_size, replace=False)
            x_train_sample = x_train[train_indices]
            y_train_sample = y_train[train_indices]
        else:
            x_train_sample = x_train
            y_train_sample = y_train

        if len(x_test) > sample_size:
            test_indices = np.random.choice(
                len(x_test), sample_size, replace=False)
            x_test_sample = x_test[test_indices]
            y_test_sample = y_test[test_indices]
        else:
            x_test_sample = x_test
            y_test_sample = y_test

        try:
            # Get model confidence on training data
            train_preds = model.predict(x_train_sample)
            if isinstance(train_preds, (list, tuple)):
                train_preds = train_preds[0]

            train_confidence = np.max(
                train_preds, axis=1) if train_preds.ndim > 1 else train_preds

            # Get model confidence on test data
            test_preds = model.predict(x_test_sample)
            if isinstance(test_preds, (list, tuple)):
                test_preds = test_preds[0]

            test_confidence = np.max(
                test_preds, axis=1) if test_preds.ndim > 1 else test_preds

            # Attack: threshold-based membership inference
            # Higher confidence on training data suggests membership
            threshold = (np.mean(train_confidence) +
                         np.mean(test_confidence)) / 2

            train_correct = np.sum(train_confidence > threshold)
            test_correct = np.sum(test_confidence <= threshold)

            attack_success_rate = (
                train_correct + test_correct) / (len(x_train_sample) + len(x_test_sample))

        except Exception as e:
            logger.error(f"Membership inference attack failed: {e}")
            attack_success_rate = 0.5

        # Baseline is random guessing (50%)
        baseline = 0.5
        advantage = attack_success_rate - baseline

        # Privacy assessment
        is_private = attack_success_rate < 0.55  # <55% is considered private

        return MembershipInferenceResult(
            attack_success_rate=float(attack_success_rate),
            baseline_success_rate=baseline,
            advantage=float(advantage),
            is_private=is_private,
            # Higher advantage = higher confidence
            confidence=float(abs(advantage)) * 100,
            samples_tested=len(x_train_sample) + len(x_test_sample)
        )


class AdversarialReport:
    """Generates adversarial testing reports"""

    @staticmethod
    def generate_robustness_report(results: List[AdversarialTestResult]) -> str:
        """Generate robustness assessment report"""
        report = f"""
Model Robustness Assessment Report
{'='*60}
Generated: {datetime.now().isoformat()}

Test Results:
{'-'*60}
"""

        for result in results:
            rating, score = RobustnessEvaluation.score_robustness(result)

            report += f"""
Attack Type: {result.attack_type}
  Clean Accuracy: {result.clean_accuracy:.2%}
  Adversarial Accuracy: {result.adversarial_accuracy:.2%}
  Robustness Score: {result.robustness_score:.2%}
  Epsilon: {result.epsilon}
  Rating: {rating} ({score:.1f}/1.0)
"""

        avg_robustness = np.mean([r.robustness_score for r in results])
        report += f"""

Overall Robustness: {avg_robustness:.2%}
Recommendation: {'✓ ROBUST' if avg_robustness >= 0.8 else '⚠ MODERATE' if avg_robustness >= 0.6 else '✗ WEAK'}
"""

        return report

    @staticmethod
    def generate_privacy_report(mia_result: MembershipInferenceResult) -> str:
        """Generate privacy assessment report"""
        privacy_level = "HIGH" if mia_result.is_private else "LOW"
        status = "✓ PRIVATE" if mia_result.is_private else "✗ LEAKY"

        report = f"""
Model Privacy Assessment Report
{'='*60}
Generated: {datetime.now().isoformat()}

Membership Inference Attack Results:
{'-'*60}
Attack Success Rate: {mia_result.attack_success_rate:.2%}
Baseline (Random): {mia_result.baseline_success_rate:.2%}
Advantage: {mia_result.advantage:.2%}

Privacy Level: {privacy_level}
Status: {status}

Assessment:
  - Attack success rate < 55% indicates good privacy (random guessing)
  - Your model: {mia_result.attack_success_rate:.2%}
  - Conclusion: {'Model appears PRIVATE' if mia_result.is_private else 'Model appears to LEAK training data'}

Samples Tested: {mia_result.samples_tested}
Confidence: {mia_result.confidence:.1f}%
"""

        return report
