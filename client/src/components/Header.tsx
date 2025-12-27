import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import { Button } from "@/components/ui/button";

const Header = () => {
  return (
    <div className="mb-6 flex justify-between">
      <h1 className="text-2xl font-bold">AI Interview Coach</h1>
      <div>
        <SignedIn>
          <UserButton
            appearance={{
              baseTheme: dark,
            }}
          />
        </SignedIn>
        <SignedOut>
          <SignInButton
            mode="modal"
            appearance={{
              baseTheme: dark,
            }}
          >
            <Button variant="default" className="font-semibold">
              Sign in
            </Button>
          </SignInButton>
        </SignedOut>
      </div>
    </div>
  );
};

export default Header;
