import { ReactNode, KeyboardEvent } from "react";
import styles from "./Badge.module.css";

type Variant = "filled" | "outline" | "selected";

interface BadgeProps {
  variant?: Variant;
  onClick?: () => void;
  children: ReactNode;
  className?: string;
}

export default function Badge({
  variant = "filled",
  onClick,
  children,
  className = "",
}: BadgeProps) {
  const isClickable = Boolean(onClick);

  const handleKeyDown = (e: KeyboardEvent<HTMLSpanElement>) => {
    if (onClick && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      onClick();
    }
  };

  return (
    <span
      className={`${styles.badge} ${styles[variant]} ${isClickable ? styles.clickable : ""} ${className}`.trim()}
      onClick={onClick}
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={isClickable ? handleKeyDown : undefined}
    >
      {children}
    </span>
  );
}
