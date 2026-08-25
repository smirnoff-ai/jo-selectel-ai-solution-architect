import { AppealWorkspace } from "@/components/appeal-workspace";

export default async function AppealPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <AppealWorkspace appealId={Number(id)} />;
}
