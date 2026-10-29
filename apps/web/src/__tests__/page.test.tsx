import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("renders the EriWatch platform heading and subtitle", () => {
    render(<HomePage />);
    expect(
      screen.getByRole("heading", {
        name: /EriWatch: Satellite Early Warning & Grievance Platform/i,
      }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Tamil Nadu Tank Intelligence/i)).toBeInTheDocument();
  });
});
