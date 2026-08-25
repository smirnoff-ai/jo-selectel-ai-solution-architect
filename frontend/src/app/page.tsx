import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function Home() {
  const jar = await cookies();
  if (jar.get("reflex_session")) {
    redirect("/desk");
  }
  redirect("/login");
}
